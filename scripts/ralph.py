#!/usr/bin/env python3
"""Compatibility wrapper for the packaged Ralph CLI."""

from __future__ import annotations

import os
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "tools" / "ralph-loop"


def main() -> None:
    """Run the packaged Ralph CLI inside its uv Subproject environment."""
    os.execvp(
        "uv",
        ["uv", "run", "--project", str(PACKAGE_ROOT), "ralph", *sys.argv[1:]],
    )


if __name__ == "__main__":
    main()
