import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Union


def get_file_hash(path: Union[str, Path], bytes_per_chunk: int = 8192) -> str:
    """Hash a file in chunks using md5."""
    path_hash = hashlib.md5()
    with open(path, "rb") as path_file:
        chunk = path_file.read(bytes_per_chunk)
        while chunk:
            path_hash.update(chunk)
            chunk = path_file.read(bytes_per_chunk)

    return path_hash.hexdigest()


# -----------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="+")
    parser.add_argument("--dir", help="Parent directory")
    args = parser.parse_args()

    if args.dir:
        args.dir = Path(args.dir)

    hashes = {}
    for path_str in args.file:
        path = Path(path_str)
        path_hash = get_file_hash(path)
        if args.dir:
            path = path.relative_to(args.dir)

        hashes[str(path)] = path_hash

    json.dump(hashes, sys.stdout)


if __name__ == "__main__":
    main()
