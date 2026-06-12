#!/usr/bin/env python3
import argparse
import logging
from pathlib import Path

import torch

from .vits.lightning import VitsModel

_LOGGER = logging.getLogger("piper_train.export_torchscript")


def main():
    """Main entry point"""
    torch.manual_seed(1234)

    parser = argparse.ArgumentParser()
    parser.add_argument("checkpoint", help="Path to model checkpoint (.ckpt)")
    parser.add_argument("output", help="Path to output model (.onnx)")

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
    args.output = Path(args.output)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    model = VitsModel.load_from_checkpoint(args.checkpoint, dataset=None)
    model_g = model.model_g

    num_symbols = model_g.n_vocab

    # Inference only
    model_g.eval()

    with torch.no_grad():
        model_g.dec.remove_weight_norm()

    model_g.forward = model_g.infer

    dummy_input_length = 50
    sequences = torch.randint(
        low=0, high=num_symbols, size=(1, dummy_input_length), dtype=torch.long
    )
    sequence_lengths = torch.LongTensor([sequences.size(1)])

    sid = torch.LongTensor([0])

    dummy_input = (
        sequences,
        sequence_lengths,
        sid,
        torch.FloatTensor([0.667]),
        torch.FloatTensor([1.0]),
        torch.FloatTensor([0.8]),
    )

    jitted_model = torch.jit.trace(model_g, dummy_input)
    torch.jit.save(jitted_model, str(args.output))

    _LOGGER.info("Saved TorchScript model to %s", args.output)


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
