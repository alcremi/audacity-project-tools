from pathlib import Path

import pytest

from audacity_project_tools.api import convert_directory, format_report
import audacity_project_tools.api as api
from audacity_project_tools.models import (ConversionDecision, ValidationResult, ConversionReport, ConversionFailure)


def test_format_report_with_failure(tmp_path: Path) -> None:

    report = ConversionReport(
        count=3,
        converted=2,
        skipped=0,
        failed=1,
        failures=[
            ConversionFailure(
                source=tmp_path / "A.aup",
                reason="Missing data directory",
            )
        ],
    )

    text = format_report(report, tmp_path)

    assert "Projects found : 3" in text
    assert "Converted      : 2" in text
    assert "Failed         : 1" in text
    assert "A.aup" in text
    assert "Missing data directory" in text

def test_format_report_without_failure(tmp_path: Path) -> None:
    report = ConversionReport(
        count=3,
        converted=2,
        skipped=0,
        failed=0,
        failures=[],
    )
    text = format_report(report, tmp_path)

    assert "Failed projects:" not in text


def fake_should_convert(source: Path) -> ValidationResult:
    return ValidationResult(
        decision=ConversionDecision.CONVERT,
    )

class FakeScanner:

    def scan(self, root: Path):
        for name in ("A.aup", "B.aup", "C.aup"):
            source = root / name
            (root / f"{source.stem}_data").mkdir()
            yield source


class FakeSession:

    def __init__(self):
        self.closed = False

    def start(self):
        return object()

    def close(self):
        self.closed = True


class FakeConverter:

    calls: list[tuple[Path, Path]] = []

    def __init__(self, client):
        pass

    def convert(
        self,
        source: Path,
        destination: Path,
    ) -> None:
        self.calls.append((source, destination))

        if source.name == "B.aup":
            raise RuntimeError("Conversion failed")


def test_convert_directory_uses_source_directory_by_default(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    FakeConverter.calls.clear()

    monkeypatch.setattr(api, "ProjectScanner", FakeScanner)
    monkeypatch.setattr(api, "AudacitySession", FakeSession)
    monkeypatch.setattr(api, "ProjectConverter", FakeConverter)

    report = convert_directory(tmp_path)

    assert report.count == 3
    assert report.converted == 2
    assert report.skipped == 0
    assert report.failed == 1

    assert FakeConverter.calls == [
        (
            tmp_path / "A.aup",
            tmp_path / "A.aup3",
        ),
        (
            tmp_path / "B.aup",
            tmp_path / "B.aup3",
        ),
        (
            tmp_path / "C.aup",
            tmp_path / "C.aup3",
        ),
    ]

def test_convert_directory_uses_output_directory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    FakeConverter.calls.clear()

    monkeypatch.setattr(api, "ProjectScanner", FakeScanner)
    monkeypatch.setattr(api, "AudacitySession", FakeSession)
    monkeypatch.setattr(api, "ProjectConverter", FakeConverter)

    output_dir = tmp_path / "converted"

    report = convert_directory(
        tmp_path,
        output_dir=output_dir,
    )

    assert report.count == 3
    assert report.converted == 2
    assert report.skipped == 0
    assert report.failed == 1

    assert FakeConverter.calls == [
        (
            tmp_path / "A.aup",
            output_dir / "A.aup3",
        ),
        (
            tmp_path / "B.aup",
            output_dir / "B.aup3",
        ),
        (
            tmp_path / "C.aup",
            output_dir / "C.aup3",
        ),
    ]

def test_convert_directory_dry_run_uses_output_directory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    FakeConverter.calls.clear()

    monkeypatch.setattr(api, "ProjectScanner", FakeScanner)
    monkeypatch.setattr(api, "AudacitySession", FakeSession)
    monkeypatch.setattr(api, "ProjectConverter", FakeConverter)

    output_dir = tmp_path / "converted"

    report = convert_directory(
        tmp_path,
        output_dir=output_dir,
        dry_run=True,
    )

    assert report.count == 3
    assert report.converted == 0
    assert report.skipped == 0
    assert report.failed == 0

    assert FakeConverter.calls == []

    captured = capsys.readouterr()

    assert (
        f"{tmp_path / 'A.aup'} -> "
        f"{output_dir / 'A.aup3'}"
    ) in captured.out

    assert (
        f"{tmp_path / 'B.aup'} -> "
        f"{output_dir / 'B.aup3'}"
    ) in captured.out

    assert (
        f"{tmp_path / 'C.aup'} -> "
        f"{output_dir / 'C.aup3'}"
    ) in captured.out
