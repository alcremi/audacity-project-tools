from pathlib import Path

import pytest

from audacity_project_tools.api import convert_directory
import audacity_project_tools.api as api
from audacity_project_tools.models import (
    ConversionDecision,
    ValidationResult,
)

def fake_should_convert(source: Path) -> ValidationResult:
    return ValidationResult(
        decision=ConversionDecision.CONVERT,
    )

class FakeScanner:

    def scan(self, root: Path):
        yield Path("A.aup")
        yield Path("B.aup")
        yield Path("C.aup")


class FakeSession:

    def __init__(self):
        self.closed = False

    def start(self):
        return object()

    def close(self):
        self.closed = True


class FakeConverter:

    calls: list[Path] = []

    def __init__(self, client):
        pass

    def convert(
        self,
        source: Path,
        destination: Path,
    ) -> None:
        self.calls.append(source)

        if source.name == "B.aup":
            raise RuntimeError("Conversion failed")


def test_convert_directory_continues_after_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    FakeConverter.calls.clear()

    monkeypatch.setattr(
        api,
        "ProjectScanner",
        FakeScanner,
    )

    monkeypatch.setattr(
        api,
        "AudacitySession",
        FakeSession,
    )

    monkeypatch.setattr(
        api,
        "ProjectConverter",
        FakeConverter,
    )

    monkeypatch.setattr(
        api,
        "should_convert",
        fake_should_convert,
    )

    report = convert_directory(
        Path("/tmp"),
    )

    assert report.count == 3
    assert report.converted == 2
    assert report.failures[0].source == Path("B.aup")
    assert "Conversion failed" in report.failures[0].reason

    assert FakeConverter.calls == [
        Path("A.aup"),
        Path("B.aup"),
        Path("C.aup"),
    ]

def test_convert_directory_does_not_start_audacity_for_skipped_projects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    class FakeScanner:
        def scan(self, root: Path):
            yield Path("A.aup")

    def fake_should_convert(source: Path) -> ValidationResult:
        return ValidationResult(
            decision=ConversionDecision.SKIP_ALREADY_CONVERTED,
            message="Project already converted.",
        )

    start_called = False

    class FakeSession:
        def start(self):
            nonlocal start_called
            start_called = True
            return object()

        def close(self):
            pass

    class FakeConverter:
        calls: list[Path] = []

        def __init__(self, client):
            pass

        def convert(
            self,
            source: Path,
            destination: Path,
        ) -> None:
            self.calls.append(source)

    monkeypatch.setattr(api, "ProjectScanner", FakeScanner)
    monkeypatch.setattr(api, "should_convert", fake_should_convert)
    monkeypatch.setattr(api, "AudacitySession", FakeSession)
    monkeypatch.setattr(api, "ProjectConverter", FakeConverter)

    report = convert_directory(Path("/tmp"))

    assert report.count == 1
    assert report.converted == 0
    assert report.skipped == 1
    assert report.failed == 0

    assert report.failures == []

    assert start_called is False
    assert FakeConverter.calls == []
