"""Bootstrap dependencies required by the standalone E2A-SML container."""

from __future__ import annotations

import os
import sys

from .voice_library import DEFAULT_REPO_ID, configured_e2a_path, ensure_voice_library


def main() -> None:
    repo_id = os.environ.get("E2A_VOICES_REPO_ID", DEFAULT_REPO_ID)
    try:
        ensure_voice_library(configured_e2a_path(), repo_id=repo_id)
    except Exception as exc:
        print(f"Unable to prepare the ebook2audiobook voice library: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    os.execvp(
        sys.executable,
        [sys.executable, "cli.py", "--gui", "--host", "0.0.0.0"],
    )


if __name__ == "__main__":
    main()
