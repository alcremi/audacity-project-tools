from __future__ import annotations

from pathlib import Path

import argparse


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="audacity-project-tools",
        description="Convert legacy Audacity projects to .aup3 format.",
    )

    parser.add_argument(
        "directory",
        metavar="DIRECTORY",
        type=Path,
        help="Directory containing Audacity projects.",
    )

    # Optional arguments will be added here.
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned conversions without modifying files.",
    )

    return parser.parse_args(argv)
