from pathlib import Path

import pytest
from unittest.mock import patch

from audacity_project_tools.exceptions import ConversionError, PipeTimeoutError
from test_pipe                         import FakePipe3
from audacity_project_tools            import AudacityClient
from audacity_project_tools            import ProjectConverter
from audacity_project_tools            import ConversionMode


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

        def load_project(
            self,
            path: Path,
            timeout: float | None = None,
        ):
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


def test_convert_aup3_to_aup3_cleans_temporary_file_on_timeout(
    tmp_path: Path,
) -> None:
    source = tmp_path / "project.aup3"
    destination = tmp_path / "output.aup3"

    source.write_bytes(b"original project")

    class FakeClient:
        def load_project(
            self,
            path: Path,
            timeout: float | None = None,
        ):
            assert path == (
                tmp_path / ".project.conversion.aup3"
            )
            assert timeout == 0.1
            raise PipeTimeoutError(
                "Timeout waiting for Audacity response."
            )

        def save_project(self, path: Path) -> None:
            raise AssertionError(
                "save_project() should not be called"
            )

    converter = ProjectConverter(
        FakeClient(),
        load_timeout=0.1,
    )

    with pytest.raises(PipeTimeoutError):
        converter.convert(
            source,
            destination,
            ConversionMode.AUP3_TO_AUP3,
        )

    assert source.read_bytes() == b"original project"
    assert not destination.exists()
    assert not (
        tmp_path / ".project.conversion.aup3"
    ).exists()


def test_convert_aup3_to_aup3_cleans_temporary_sidecar_files(
    tmp_path: Path,
) -> None:
    source = tmp_path / "project.aup3"
    destination = tmp_path / "output.aup3"

    source.write_bytes(b"original project")

    temporary = tmp_path / ".project.conversion.aup3"

    class FakeClient:
        def load_project(
            self,
            path: Path,
            timeout: float | None = None,
        ):
            assert path == temporary

            for suffix in ("", "-shm", "-wal"):
                Path(f"{path}{suffix}").touch()

            raise PipeTimeoutError(
                "Timeout waiting for Audacity response."
            )

        def save_project(self, path: Path) -> None:
            raise AssertionError(
                "save_project() should not be called"
            )

    converter = ProjectConverter(
        FakeClient(),
        load_timeout=0.1,
    )

    with pytest.raises(PipeTimeoutError):
        converter.convert(
            source,
            destination,
            ConversionMode.AUP3_TO_AUP3,
        )

    assert not temporary.exists()
    assert not Path(f"{temporary}-shm").exists()
    assert not Path(f"{temporary}-wal").exists()


def test_convert_aup3_to_aup3_cleans_temporary_files_on_save_failure(
    tmp_path: Path,
) -> None:
    source = tmp_path / "project.aup3"
    destination = tmp_path / "output.aup3"

    source.write_bytes(b"original project")

    temporary = tmp_path / ".project.conversion.aup3"

    class FakeClient:
        def load_project(
            self,
            path: Path,
            timeout: float | None = None,
        ):
            assert path == temporary

            for suffix in ("", "-shm", "-wal"):
                Path(f"{path}{suffix}").touch()

            return object()

        def save_project(self, path: Path) -> None:
            raise RuntimeError("Save failed")

    converter = ProjectConverter(FakeClient())

    with pytest.raises(RuntimeError, match="Save failed"):
        converter.convert(
            source,
            destination,
            ConversionMode.AUP3_TO_AUP3,
        )

    assert source.read_bytes() == b"original project"
    assert not destination.exists()

    assert not temporary.exists()
    assert not Path(f"{temporary}-shm").exists()
    assert not Path(f"{temporary}-wal").exists()


def test_convert_waits_until_destination_is_created(
    tmp_path: Path,
) -> None:
    source = tmp_path / "project.aup"
    destination = tmp_path / "output.aup3"

    source.touch()

    class FakeClient:
        def load_project(
            self,
            path: Path,
            timeout: float | None = None,
        ):
            return object()

        def save_project(self, path: Path) -> None:
            pass

    converter = ProjectConverter(
        FakeClient(),
        save_timeout=1.0,
    )

    real_exists = Path.exists
    checks = 0

    def fake_exists(path: Path) -> bool:
        nonlocal checks

        if path == destination:
            checks += 1

            if checks >= 2:
                return True

            return False

        return real_exists(path)

    with patch.object(
        Path,
        "exists",
        fake_exists,
    ):
        converter.convert(
            source,
            destination,
            ConversionMode.AUP_TO_AUP3,
        )

    assert checks == 2


def test_convert_aup3_to_aup3_propagates_copy_error(
    tmp_path: Path,
) -> None:
    source = tmp_path / "project.aup3"
    destination = tmp_path / "output.aup3"

    source.write_bytes(b"original project")

    class FakeClient:
        def load_project(
            self,
            path: Path,
            timeout: float | None = None,
        ):
            raise AssertionError(
                "load_project() should not be called"
            )

        def save_project(self, path: Path) -> None:
            raise AssertionError(
                "save_project() should not be called"
            )

    converter = ProjectConverter(FakeClient())

    with patch(
        "audacity_project_tools.converter.shutil.copy2",
        side_effect=OSError("Copy failed"),
    ):
        with pytest.raises(OSError, match="Copy failed"):
            converter.convert(
                source,
                destination,
                ConversionMode.AUP3_TO_AUP3,
            )

    assert source.read_bytes() == b"original project"
    assert not destination.exists()
