from pathlib import Path

import pytest

from audacity_project_tools.cli import parse_args

def test_parse_directory() -> None:
    args = parse_args(["/tmp"])

    assert args.directory == Path("/tmp")


def test_help() -> None:

    with pytest.raises(SystemExit):
        parse_args(["--help"])


def test_dry_run() -> None:
    args = parse_args([
        "--dry-run",
        "/tmp",
    ])

    assert args.dry_run is True


def test_no_dry_run() -> None:
    args = parse_args([
        "/tmp",
    ])

    assert args.dry_run is False
