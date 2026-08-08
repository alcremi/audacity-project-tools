from pathlib import Path

from audacity_project_tools.models    import ConversionDecision, ValidationResult
from audacity_project_tools.validator import should_convert

ALREADY_CONVERTED = "Project already converted."
MISSING_DATA = "Missing data directory"

def test_should_convert_returns_convert(tmp_path: Path) -> None:
    source = tmp_path / "project.aup"
    destination = tmp_path / "project.aup3"

    data_dir = tmp_path / "project_data"
    data_dir.mkdir()

    result = should_convert(source, destination)

    assert result.decision == ConversionDecision.CONVERT

def test_should_convert_returns_skip_if_destination_exists(
    tmp_path: Path,
) -> None:
    source = tmp_path / "project.aup"
    destination = tmp_path / "project.aup3"

    data_dir = tmp_path / "project_data"
    data_dir.mkdir()

    destination.touch()

    result = should_convert(source, destination)

    assert result.decision == ConversionDecision.SKIP_ALREADY_CONVERTED


def test_should_convert_returns_fail_if_data_missing(
    tmp_path: Path,
) -> None:
    source = tmp_path / "project.aup"
    destination = tmp_path / "project.aup3"

    result = should_convert(source, destination)

    assert result.decision == ConversionDecision.FAIL_MISSING_DATA


def test_should_convert_reports_missing_data(
    tmp_path: Path,
) -> None:
    source = tmp_path / "project.aup"
    destination = tmp_path / "project.aup3"

    result = should_convert(source, destination)

    assert result.message == "Missing data directory: project_data"


def test_should_convert_uses_destination_path(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source" / "project.aup"
    destination = tmp_path / "converted" / "project.aup3"

    source.parent.mkdir()
    destination.parent.mkdir()

    data_dir = source.with_name("project_data")
    data_dir.mkdir()

    destination.touch()

    result = should_convert(source, destination)

    assert result.decision == ConversionDecision.SKIP_ALREADY_CONVERTED
