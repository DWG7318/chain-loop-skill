#!/usr/bin/env python3
"""Regenerate the deterministic CLK release hash manifest."""

from __future__ import annotations

import json
from pathlib import Path

from validate_repository import ROOT, release_files, sha256


def main() -> int:
    hashes = {
        path.relative_to(ROOT).as_posix(): sha256(path)
        for path in release_files(ROOT)
    }
    (ROOT / "FILE_HASHES.json").write_text(
        json.dumps(hashes, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"UPDATED: FILE_HASHES.json ({len(hashes)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
