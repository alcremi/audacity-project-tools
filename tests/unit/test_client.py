from pathlib import Path
import time
import pytest
from unittest.mock import patch

from audacity_project_tools            import AudacityPipe, AudacityClient, Track
from test_pipe                         import FakePipe3, FakePipe4
from audacity_project_tools.exceptions import PipeTimeoutError, AudacityCommandError


def test_client() -> None:
    pipe = FakePipe()
    client = AudacityClient(pipe)
    client.help()
    assert pipe.command == "Help:"



class FakePipe:
    def __init__(self) -> None:
        self.command = ""

    def send(
        self,
        command: str,
        timeout: float | None = None,
    ) -> str:
        self.command = command
        return "BatchCommand finished: OK"


def test_help_command() -> None:
    pipe = FakePipe()
    client = AudacityClient(pipe)

    client.help()

    assert pipe.command == "Help:"


class FakePipe2:
    def __init__(self) -> None:
        self.command = ""

    def send(
        self,
        command: str,
        timeout: float | None = None,
    ) -> str:
        self.command = command
        return """
[
    {
        "name": "Voice",
        "kind": "wave",
        "start": 0,
        "end": 12.5,
        "channels": 1
    }
]
"""

def test_get_tracks_command() -> None:
    pipe = FakePipe2()
    client = AudacityClient(pipe)

    tracks = client.get_tracks()

    assert pipe.command == "GetInfo: Type=Tracks"
    assert len(tracks) == 1



def test_open_project() -> None:

    pipe = FakePipe4()
    client = AudacityClient(pipe)

    client.open_project(Path("/tmp/test.aup"))

    assert pipe.commands == [
        'OpenProject2: Filename="/tmp/test.aup"',
        "GetInfo: Type=Tracks",
        "GetInfo: Type=Tracks",
        "GetInfo: Type=Tracks",
    ]

def test_save_project() -> None:

    pipe = FakePipe3()
    client = AudacityClient(pipe)

    client.save_project(Path("/tmp/output.aup3"))

    assert pipe.commands[-1] == (
        'SaveProject2: Filename="/tmp/output.aup3"'
    )

def test_exit_audacity() -> None:

    pipe = FakePipe3()
    client = AudacityClient(pipe)

    client.exit_audacity()

    assert pipe.commands[-1] == (
        'Exit:'
    )

def test_load_project() -> None:

    pipe = FakePipe3()
    client = AudacityClient(pipe)

    project = client.load_project(Path("/tmp/test.aup"))

    assert project.path == Path("/tmp/test.aup")
    assert len(project.tracks) == 1
    assert project.tracks[0].name == "Voice"


class BlockingPipe:
    def send(self, command: str) -> str:
        if command == "GetInfo: Type=Tracks":
            time.sleep(10)
        return ""

class TimeoutPipe:
    def send(
        self,
        command: str,
        timeout: float | None = None,
    ) -> str:
        raise PipeTimeoutError(
            "Timeout waiting for Audacity response."
        )

def test_open_project_propagates_pipe_timeout() -> None:
    pipe = TimeoutPipe()
    client = AudacityClient(pipe)

    with pytest.raises(PipeTimeoutError):
        client.open_project(
            Path("/tmp/test.aup3"),
            timeout=0.1,
        )


def test_execute_returns_clean_response() -> None:
    class FakePipe:
        def send(
            self,
            command: str,
            timeout: float | None = None,
        ) -> str:
            assert command == "Help:"
            return "help text\nBatchCommand finished: OK\n"

    client = AudacityClient(FakePipe())

    response = client._execute("Help:")

    assert response == "help text\n"


def test_execute_raises_on_failed_command() -> None:
    class FakePipe:
        def send(
            self,
            command: str,
            timeout: float | None = None,
        ) -> str:
            return "BatchCommand finished: Failed!\n"

    client = AudacityClient(FakePipe())

    with pytest.raises(AudacityCommandError):
        client._execute("SomeCommand:")


def test_get_tracks_calls_parse_tracks() -> None:
    class FakePipe:
        def send(
            self,
            command: str,
            timeout: float | None = None,
        ) -> str:
            assert command == "GetInfo: Type=Tracks"
            return "tracks response\n"

    client = AudacityClient(FakePipe())

    expected_tracks = [
        Track(
            name="Track 1",
            start=0.0,
            end=10.0,
            channels=2,
        ),
    ]

    with patch(
        "audacity_project_tools.client.parse_tracks",
        return_value=expected_tracks,
    ) as mock_parse:
        tracks = client.get_tracks(timeout=3.0)

    mock_parse.assert_called_once_with("tracks response\n")
    assert tracks == expected_tracks


def test_open_project_sends_command_and_waits(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project.aup3"

    class FakePipe:
        def __init__(self) -> None:
            self.commands: list[str] = []

        def send(
            self,
            command: str,
            timeout: float | None = None,
        ) -> str:
            self.commands.append(command)
            return "BatchCommand finished: OK\n"

    pipe = FakePipe()
    client = AudacityClient(pipe)

    with patch.object(
        client,
        "_wait_until_project_loaded",
    ) as wait_for_project:
        client.open_project(
            project,
            timeout=5.0,
        )

    assert pipe.commands == [
        f'OpenProject2: Filename="{project}"',
    ]

    wait_for_project.assert_called_once()


def test_wait_until_project_loaded_returns_when_tracks_are_available() -> None:
    pipe = FakePipe()
    client = AudacityClient(pipe)

    with patch.object(
        client,
        "get_tracks",
        return_value=[],
    ) as get_tracks:
        client._wait_until_project_loaded()

    get_tracks.assert_called_once()


def test_wait_until_project_loaded_retries_after_command_error() -> None:
    client = AudacityClient(None)  # type: ignore[arg-type]

    calls = 0

    def fake_get_tracks(
        timeout: float | None = None,
    ) -> list[Track]:
        nonlocal calls
        calls += 1

        if calls < 3:
            raise AudacityCommandError("Project not ready")

        return []

    with patch.object(
        client,
        "get_tracks",
        side_effect=fake_get_tracks,
    ):
        with patch(
            "audacity_project_tools.client.time.sleep"
        ) as sleep:
            client._wait_until_project_loaded()

    assert calls == 3
    assert sleep.call_count == 2


def test_wait_until_project_loaded_times_out() -> None:
    client = AudacityClient(None)  # type: ignore[arg-type]

    with patch.object(
        client,
        "get_tracks",
        side_effect=AudacityCommandError("Project not ready"),
    ):
        with patch(
            "audacity_project_tools.client.time.monotonic",
            side_effect=[0.0, 10.1],
        ):
            with patch(
                "audacity_project_tools.client.time.sleep"
            ) as sleep:
                with pytest.raises(
                    AudacityCommandError,
                    match="Timed out while waiting for the project to load.",
                ):
                    client._wait_until_project_loaded()


def test_load_project_opens_project_gets_tracks_and_returns_project(
    tmp_path: Path,
) -> None:
    project_path = tmp_path / "project.aup3"

    client = AudacityClient(None)  # type: ignore[arg-type]

    tracks = [
        Track(
            name="Track 1",
            start=0.0,
            end=10.0,
            channels=2,
        ),
    ]

    with patch.object(
        client,
        "open_project",
    ) as open_project:
        with patch.object(
            client,
            "get_tracks",
            return_value=tracks,
        ) as get_tracks:
            project = client.load_project(
                project_path,
                timeout=7.0,
            )

    open_project.assert_called_once_with(
        project_path,
        timeout=7.0,
    )

    get_tracks.assert_called_once_with(
        timeout=7.0,
    )

    assert project.path == project_path
    assert project.tracks == tracks
