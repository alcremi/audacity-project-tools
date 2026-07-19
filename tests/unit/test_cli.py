from pathlib import Path

import pytest

from audacity_project_tools.cli import parse_args

def test_parse_directory() -> None:
    args = parse_args(["/tmp"])

    assert args.directory == Path("/tmp")

def test_help() -> None:

    with pytest.raises(SystemExit):
        parse_args(["--help"])
