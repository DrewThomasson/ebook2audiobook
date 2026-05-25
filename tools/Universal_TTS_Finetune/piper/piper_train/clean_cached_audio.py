#!/usr/bin/env python3
import argparse
from concurrent.futures import ThreadPoolExecutor
import logging
from pathlib import Path

import torch

_LOGGER = logging.getLogger()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cache-dir",
        required=True,
        help="Path to directory with audio/spectrogram files (*.pt)",
    )
    parser.add_argument(
        "--delete", action="store_true", help="Delete files that fail to load"
    )
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    _LOGGER.debug(args)

    cache_dir = Path(args.cache_dir)
    num_deleted = 0

    def check_file(pt_path: Path) -> None:
        nonlocal num_deleted

        try:
            _LOGGER.debug("Checking %s", pt_path)
            torch.load(str(pt_path))
        except Exception:
            _LOGGER.error(pt_path)
            if args.delete:
                pt_path.unlink()
                num_deleted += 1

    with ThreadPoolExecutor() as executor:
        for pt_path in cache_dir.glob("*.pt"):
            executor.submit(check_file, pt_path)

    print("Deleted:", num_deleted, "file(s)")


if __name__ == "__main__":
    main()
