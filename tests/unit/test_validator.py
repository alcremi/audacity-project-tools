from pathlib import Path

from audacity_project_tools.models    import ConversionDecision, ValidationResult
from audacity_project_tools.validator import should_convert

ALREADY_CONVERTED = "Project already converted."
MISSING_DATA = "Missing data directory"

def test_should_convert_returns_convert(tmp_path: Path) -> None:
    source = tmp_path / "project.aup"
    source.touch()

    (tmp_path / "project_data").mkdir()

    result = should_convert(source)

    assert result.decision is ConversionDecision.CONVERT
    assert result.message is None


def test_should_convert_skips_existing_aup3(tmp_path: Path) -> None:
    source = tmp_path / "project.aup"
    source.touch()

    (tmp_path / "project.aup3").touch()
    (tmp_path / "project_data").mkdir()

    result = should_convert(source)

    assert result.decision is ConversionDecision.SKIP_ALREADY_CONVERTED
    assert result.message == ALREADY_CONVERTED


def test_should_convert_detects_missing_data_directory(
    tmp_path: Path,
) -> None:
    source = tmp_path / "project.aup"
    source.touch()

    result = should_convert(source)

    assert result.decision is ConversionDecision.FAIL_MISSING_DATA
    assert "project_data" in result.message


def test_should_convert_prefers_skip_over_missing_data(
    tmp_path: Path,
) -> None:
    source = tmp_path / "project.aup"
    source.touch()

    (tmp_path / "project.aup3").touch()

    result = should_convert(source)

    assert result.decision is (
        ConversionDecision.SKIP_ALREADY_CONVERTED
    )
