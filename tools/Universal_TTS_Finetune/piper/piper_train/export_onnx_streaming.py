#!/usr/bin/env python3

import argparse
import logging
import os
from pathlib import Path
from typing import Optional

import torch
from torch import nn

from .vits import commons
from .vits.lightning import VitsModel

_LOGGER = logging.getLogger("piper_train.export_onnx")
OPSET_VERSION = 15


class VitsEncoder(nn.Module):
    def __init__(self, gen):
        super().__init__()
        self.gen = gen

    def forward(self, x, x_lengths, scales, sid=None):
        noise_scale = scales[0]
        length_scale = scales[1]
        noise_scale_w = scales[2]

        gen = self.gen
        x, m_p, logs_p, x_mask = gen.enc_p(x, x_lengths)
        if gen.n_speakers > 1:
            assert sid is not None, "Missing speaker id"
            g = gen.emb_g(sid).unsqueeze(-1)  # [b, h, 1]
        else:
            g = None

        if gen.use_sdp:
            logw = gen.dp(x, x_mask, g=g, reverse=True, noise_scale=noise_scale_w)
        else:
            logw = gen.dp(x, x_mask, g=g)
        w = torch.exp(logw) * x_mask * length_scale
        w_ceil = torch.ceil(w)
        y_lengths = torch.clamp_min(torch.sum(w_ceil, [1, 2]), 1).long()
        y_mask = torch.unsqueeze(
            commons.sequence_mask(y_lengths, y_lengths.max()), 1
        ).type_as(x_mask)
        attn_mask = torch.unsqueeze(x_mask, 2) * torch.unsqueeze(y_mask, -1)
        attn = commons.generate_path(w_ceil, attn_mask)

        m_p = torch.matmul(attn.squeeze(1), m_p.transpose(1, 2)).transpose(
            1, 2
        )  # [b, t', t], [b, t, d] -> [b, d, t']
        logs_p = torch.matmul(attn.squeeze(1), logs_p.transpose(1, 2)).transpose(
            1, 2
        )  # [b, t', t], [b, t, d] -> [b, d, t']

        z_p = m_p + torch.randn_like(m_p) * torch.exp(logs_p) * noise_scale
        return z_p, y_mask, g


class VitsDecoder(nn.Module):
    def __init__(self, gen):
        super().__init__()
        self.gen = gen

    def forward(self, z, y_mask, g=None):
        z = self.gen.flow(z, y_mask, g=g, reverse=True)
        output = self.gen.dec((z * y_mask), g=g)
        return output


def main() -> None:
    """Main entry point"""
    torch.manual_seed(1234)

    parser = argparse.ArgumentParser()
    parser.add_argument("checkpoint", help="Path to model checkpoint (.ckpt)")
    parser.add_argument("output_dir", help="Path to output directory")

    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to the console"
    )
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    _LOGGER.debug(args)

    # -------------------------------------------------------------------------

    args.checkpoint = Path(args.checkpoint)
    args.output_dir = Path(args.output_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    model = VitsModel.load_from_checkpoint(args.checkpoint, dataset=None)
    model_g = model.model_g

    with torch.no_grad():
        model_g.dec.remove_weight_norm()

    _LOGGER.info("Exporting encoder...")
    decoder_input = export_encoder(args, model_g)
    _LOGGER.info("Exporting decoder...")
    export_decoder(args, model_g, decoder_input)
    _LOGGER.info("Exported model to  %s", str(args.output_dir))


def export_encoder(args, model_g):
    model = VitsEncoder(model_g)
    model.eval()

    num_symbols = model_g.n_vocab
    num_speakers = model_g.n_speakers

    dummy_input_length = 50
    sequences = torch.randint(
        low=0, high=num_symbols, size=(1, dummy_input_length), dtype=torch.long
    )
    sequence_lengths = torch.LongTensor([sequences.size(1)])

    sid: Optional[torch.LongTensor] = None
    if num_speakers > 1:
        sid = torch.LongTensor([0])

    # noise, noise_w, length
    scales = torch.FloatTensor([0.667, 1.0, 0.8])
    dummy_input = (sequences, sequence_lengths, scales, sid)

    output_names = [
        "z",
        "y_mask",
    ]
    if model_g.n_speakers > 1:
        output_names.append("g")

    onnx_path = os.fspath(args.output_dir.joinpath("encoder.onnx"))

    # Export
    torch.onnx.export(
        model=model,
        args=dummy_input,
        f=onnx_path,
        verbose=False,
        opset_version=OPSET_VERSION,
        input_names=["input", "input_lengths", "scales", "sid"],
        output_names=output_names,
        dynamic_axes={
            "input": {0: "batch_size", 1: "phonemes"},
            "input_lengths": {0: "batch_size"},
            "output": {0: "batch_size", 2: "time"},
        },
    )
    _LOGGER.info("Exported encoder to %s", onnx_path)

    return model(*dummy_input)


def export_decoder(args, model_g, decoder_input):
    model = VitsDecoder(model_g)
    model.eval()

    input_names = [
        "z",
        "y_mask",
    ]
    if model_g.n_speakers > 1:
        input_names.append("g")

    onnx_path = os.fspath(args.output_dir.joinpath("decoder.onnx"))

    # Export
    torch.onnx.export(
        model=model,
        args=decoder_input,
        f=onnx_path,
        verbose=False,
        opset_version=OPSET_VERSION,
        input_names=input_names,
        output_names=["output"],
        dynamic_axes={
            "z": {0: "batch_size", 2: "time"},
            "y_mask": {0: "batch_size", 2: "time"},
            "output": {0: "batch_size", 1: "time"},
        },
    )

    _LOGGER.info("Exported decoder to %s", onnx_path)


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
