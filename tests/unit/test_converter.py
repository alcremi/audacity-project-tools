from pathlib import Path

import pytest

from audacity_project_tools.exceptions import ConversionError
from test_pipe              import FakePipe3
from audacity_project_tools import AudacityClient
from audacity_project_tools import ProjectConverter


def test_converter_creation() -> None:
    pipe = FakePipe3()

    client = AudacityClient(pipe)

    converter = ProjectConverter(client)

    assert converter is not None


def test_converter_convert() -> None:
    pipe = FakePipe3()

    client = AudacityClient(pipe)

    converter = ProjectConverter(client)


def test_convert_succeeds_when_destination_is_created(
    tmp_path: Path,
) -> None:
    source = tmp_path / "project.aup"
    destination = tmp_path / "project.aup3"

    source.touch()

    class FakeClient:
        def load_project(self, path: Path):
            return object()

        def save_project(self, path: Path) -> None:
            path.touch()

    converter = ProjectConverter(FakeClient())

    converter.convert(source, destination)

    assert destination.exists()


def test_convert_fails_when_destination_is_not_created(
    tmp_path: Path,
) -> None:
    source = tmp_path / "project.aup"
    destination = tmp_path / "project.aup3"

    source.touch()

    class FakeClient:
        def load_project(self, path: Path):
            return object()

        def save_project(self, path: Path) -> None:
            pass

    converter = ProjectConverter(
        FakeClient(),
        save_timeout=0.1,
    )

    with pytest.raises(ConversionError):
        converter.convert(source, destination)

    assert not destination.exists()
