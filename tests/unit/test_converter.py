from pathlib import Path

import pytest

from audacity_project_tools.exceptions import ConversionError
from test_pipe              import FakePipe3
from audacity_project_tools import AudacityClient
from audacity_project_tools import ProjectConverter
from audacity_project_tools import ConversionMode


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

    converter.convert(source, destination, ConversionMode.AUP_TO_AUP3)

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
        converter.convert(source, destination, ConversionMode.AUP_TO_AUP3)

    assert not destination.exists()


def test_convert_aup3_to_aup3_uses_temporary_copy(
    tmp_path: Path,
) -> None:
    source = tmp_path / "project.aup3"
    destination = tmp_path / "converted.aup3"

    source.write_bytes(b"original project")

    class FakeClient:
        loaded_path: Path | None = None
        loaded_content: bytes | None = None
        saved_path: Path | None = None

        def load_project(self, path: Path):
            self.loaded_path = path
            self.loaded_content = path.read_bytes()
            return object()

        def save_project(self, path: Path) -> None:
            self.saved_path = path
            path.touch()

    client = FakeClient()
    converter = ProjectConverter(client)

    converter.convert(
        source,
        destination,
        ConversionMode.AUP3_TO_AUP3,
    )

    assert client.loaded_path is not None
    assert client.loaded_path != source

    assert client.loaded_content == b"original project"

    assert client.saved_path == destination
    assert destination.exists()

    assert source.read_bytes() == b"original project"
