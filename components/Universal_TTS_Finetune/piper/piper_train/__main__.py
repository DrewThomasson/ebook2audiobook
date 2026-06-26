import argparse
import json
import logging
from pathlib import Path

import torch
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import ModelCheckpoint

from .vits.lightning import VitsModel

_LOGGER = logging.getLogger(__package__)


def main():
    import pathlib
    try:
        torch.serialization.add_safe_globals([pathlib.PosixPath, pathlib.WindowsPath])
    except AttributeError:
        pass

    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset-dir", required=True, help="Path to pre-processed dataset directory"
    )
    parser.add_argument(
        "--checkpoint-epochs",
        type=int,
        help="Save checkpoint every N epochs (default: 1)",
    )
    parser.add_argument(
        "--quality",
        default="medium",
        choices=("x-low", "medium", "high"),
        help="Quality/size of model (default: medium)",
    )
    parser.add_argument(
        "--resume_from_single_speaker_checkpoint",
        help="For multi-speaker models only. Converts a single-speaker checkpoint to multi-speaker and resumes training",
    )
    parser.add_argument("--max_epochs", type=int, help="Max number of epochs to train")
    parser.add_argument("--accelerator", type=str, help="Accelerator to use (cpu, gpu, mps, auto)")
    parser.add_argument("--devices", type=str, help="Devices to use (e.g., number of gpus or 'auto')")
    parser.add_argument("--precision", type=str, default="32", help="Precision to use (e.g. 16, 32, bf16)")
    parser.add_argument("--default_root_dir", type=str, help="Default path for logs and checkpoints")
    parser.add_argument("--resume_from_checkpoint", type=str, help="Resume training from a checkpoint")
    VitsModel.add_model_specific_args(parser)
    parser.add_argument("--seed", type=int, default=1234)
    args = parser.parse_args()
    _LOGGER.debug(args)

    args.dataset_dir = Path(args.dataset_dir)
    if not args.default_root_dir:
        args.default_root_dir = args.dataset_dir

    torch.backends.cudnn.benchmark = True
    torch.manual_seed(args.seed)

    config_path = args.dataset_dir / "config.json"
    dataset_path = args.dataset_dir / "dataset.jsonl"

    with open(config_path, "r", encoding="utf-8") as config_file:
        # See preprocess.py for format
        config = json.load(config_file)
        num_symbols = int(config["num_symbols"])
        num_speakers = int(config["num_speakers"])
        sample_rate = int(config["audio"]["sample_rate"])

    checkpoint_epoch = 0
    if args.resume_from_checkpoint:
        try:
            ckpt = torch.load(args.resume_from_checkpoint, map_location="cpu", weights_only=True)
            checkpoint_epoch = ckpt.get("epoch", 0)
            _LOGGER.info("Resuming from checkpoint epoch: %s", checkpoint_epoch)
        except Exception as e:
            _LOGGER.warning("Could not read epoch from checkpoint: %s", e)

    trainer_kwargs = {}
    if args.max_epochs is not None:
        trainer_kwargs["max_epochs"] = checkpoint_epoch + args.max_epochs
    if args.accelerator is not None:
        trainer_kwargs["accelerator"] = args.accelerator
    if args.devices is not None:
        try:
            trainer_kwargs["devices"] = int(args.devices)
        except ValueError:
            trainer_kwargs["devices"] = args.devices
    if args.precision is not None:
        trainer_kwargs["precision"] = args.precision
    if args.default_root_dir is not None:
        trainer_kwargs["default_root_dir"] = args.default_root_dir

    callbacks = []
    if args.checkpoint_epochs is not None:
        callbacks.append(
            ModelCheckpoint(
                every_n_epochs=args.checkpoint_epochs,
                save_on_train_epoch_end=True,
                save_last=True,
                dirpath=Path(args.default_root_dir),
                filename="epoch={epoch}-step={step}",
            )
        )
        _LOGGER.debug(
            "Checkpoints will be saved every %s epoch(s)", args.checkpoint_epochs
        )
    trainer_kwargs["callbacks"] = callbacks

    trainer = Trainer(**trainer_kwargs)

    dict_args = vars(args)
    if args.quality == "x-low":
        dict_args["hidden_channels"] = 96
        dict_args["inter_channels"] = 96
        dict_args["filter_channels"] = 384
    elif args.quality == "high":
        dict_args["resblock"] = "1"
        dict_args["resblock_kernel_sizes"] = (3, 7, 11)
        dict_args["resblock_dilation_sizes"] = (
            (1, 3, 5),
            (1, 3, 5),
            (1, 3, 5),
        )
        dict_args["upsample_rates"] = (8, 8, 2, 2)
        dict_args["upsample_initial_channel"] = 512
        dict_args["upsample_kernel_sizes"] = (16, 16, 4, 4)

    model = VitsModel(
        num_symbols=num_symbols,
        num_speakers=num_speakers,
        sample_rate=sample_rate,
        dataset=[dataset_path],
        **dict_args,
    )

    if args.resume_from_single_speaker_checkpoint:
        assert (
            num_speakers > 1
        ), "--resume_from_single_speaker_checkpoint is only for multi-speaker models. Use --resume_from_checkpoint for single-speaker models."

        # Load single-speaker checkpoint
        _LOGGER.debug(
            "Resuming from single-speaker checkpoint: %s",
            args.resume_from_single_speaker_checkpoint,
        )
        model_single = VitsModel.load_from_checkpoint(
            args.resume_from_single_speaker_checkpoint,
            dataset=None,
        )
        g_dict = model_single.model_g.state_dict()
        for key in list(g_dict.keys()):
            # Remove keys that can't be copied over due to missing speaker embedding
            if (
                key.startswith("dec.cond")
                or key.startswith("dp.cond")
                or ("enc.cond_layer" in key)
            ):
                g_dict.pop(key, None)

        # Copy over the multi-speaker model, excluding keys related to the
        # speaker embedding (which is missing from the single-speaker model).
        load_state_dict(model.model_g, g_dict)
        load_state_dict(model.model_d, model_single.model_d.state_dict())
        _LOGGER.info(
            "Successfully converted single-speaker checkpoint to multi-speaker"
        )

    trainer.fit(model, ckpt_path=args.resume_from_checkpoint)
    final_ckpt_path = Path(args.default_root_dir) / "epoch=final.ckpt"
    trainer.save_checkpoint(final_ckpt_path)
    _LOGGER.info("Manually saved final checkpoint to: %s", final_ckpt_path)


def load_state_dict(model, saved_state_dict):
    state_dict = model.state_dict()
    new_state_dict = {}

    for k, v in state_dict.items():
        if k in saved_state_dict:
            # Use saved value
            new_state_dict[k] = saved_state_dict[k]
        else:
            # Use initialized value
            _LOGGER.debug("%s is not in the checkpoint", k)
            new_state_dict[k] = v

    model.load_state_dict(new_state_dict)


# -----------------------------------------------------------------------------


if __name__ == "__main__":
    main()
