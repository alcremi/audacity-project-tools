from __future__ import annotations

from pathlib import Path

import argparse

from .models import ConversionMode


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

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging.",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory where converted projects are written.",
    )

    parser.add_argument(
        "--mode",
        type=ConversionMode,
        choices=list(ConversionMode),
        default=ConversionMode.AUP_TO_AUP3,
        metavar="{aup-to-aup3,aup3-to-aup3}",
        help="Conversion mode.",
    )

    return parser.parse_args(argv)


def validate_args(args: argparse.Namespace) -> None:
    """Validate command-line arguments."""

    if (
        args.mode == ConversionMode.AUP3_TO_AUP3
        and args.output_dir is None
    ):
        raise ValueError(
            "--output-dir is required with --mode aup3-to-aup3"
        )
