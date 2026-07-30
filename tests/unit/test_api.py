from pathlib import Path

import pytest

from audacity_project_tools.api import convert_directory
import audacity_project_tools.api as api


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
