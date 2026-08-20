from pathlib import Path

import pytest

from audacity_project_tools.cli    import parse_args, validate_args
from audacity_project_tools.models import ConversionMode


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


def test_parse_args_defaults_to_aup_to_aup3() -> None:
    args = parse_args(["/tmp/projects"])

    assert args.mode == ConversionMode.AUP_TO_AUP3


def test_parse_args_accepts_aup_to_aup3() -> None:
    args = parse_args(
        [
            "/tmp/projects",
            "--mode",
            "aup-to-aup3",
        ]
    )

    assert args.mode == ConversionMode.AUP_TO_AUP3


def test_parse_args_accepts_aup3_to_aup3() -> None:
    args = parse_args(
        [
            "/tmp/projects",
            "--mode",
            "aup3-to-aup3",
        ]
    )

    assert args.mode == ConversionMode.AUP3_TO_AUP3


def test_parse_args_rejects_unknown_mode() -> None:
    with pytest.raises(SystemExit):
        parse_args(
            [
                "/tmp/projects",
                "--mode",
                "something-else",
            ]
        )


def test_parse_args_accepts_aup3_to_aup3_without_output_dir() -> None:
    args = parse_args(
        [
            "/tmp/projects",
            "--mode",
            "aup3-to-aup3",
        ]
    )

    assert args.mode == ConversionMode.AUP3_TO_AUP3
    assert args.output_dir is None


def test_validate_args_rejects_aup3_to_aup3_without_output_dir() -> None:
    args = parse_args(
        [
            "/tmp/projects",
            "--mode",
            "aup3-to-aup3",
        ]
    )

    with pytest.raises(
        ValueError,
        match="--output-dir is required",
    ):
        validate_args(args)


def test_validate_args_accepts_aup3_to_aup3_with_output_dir(
    tmp_path: Path,
) -> None:
    args = parse_args(
        [
            "/tmp/projects",
            "--mode",
            "aup3-to-aup3",
            "--output-dir",
            str(tmp_path),
        ]
    )

    validate_args(args)


def test_validate_args_accepts_aup_to_aup3_without_output_dir() -> None:
    args = parse_args(
        [
            "/tmp/projects",
            "--mode",
            "aup-to-aup3",
        ]
    )

    validate_args(args)


def test_debug() -> None:
    args = parse_args([
        "--debug",
        "/tmp",
    ])

    assert args.debug is True


def test_no_debug() -> None:
    args = parse_args([
        "/tmp",
    ])

    assert args.debug is False
