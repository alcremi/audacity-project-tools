from pathlib import Path
import time
import pytest
import os
import threading
from unittest.mock import patch

from audacity_project_tools.exceptions import PipeTimeoutError, PipeConnectionError
from audacity_project_tools.pipe       import AudacityPipe, PIPE_TO, PIPE_FROM


class FakePipe:
    def __init__(self) -> None:
        self.command = "Help:"

    def _sendHelp(self, command: str) -> str:
        self.command = command
        return "BatchCommand finished: OK"

    def send(
        self,
        command: str,
        timeout: float | None = None,
    ) -> str:
        if str == "Help:":
            self.command = "Help:"
            return self._sendHelp(command)

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

class FakePipe3:
    def __init__(self) -> None:
        self.command = ""
        self.commands: list[str] = []

    def _sendHelp(self, command: str) -> str:
        self.command = command
        return "BatchCommand finished: OK"

    def send(
        self,
        command: str,
        timeout: float | None = None,
    ) -> str:
        self.command = command
        self.commands.append(command)
        if command == "Help:":
            self.command = "Help:"
            return self._sendHelp(command)
        if command != "GetInfo: Type=Tracks":
            return "BatchCommand finished: OK"
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


class FakePipe4:
    def __init__(self) -> None:
        self.commands: list[str] = []
        self.responses = iter([
            "BatchCommand finished: Failed!",
            "BatchCommand finished: Failed!",
            """
[
    {
        "name": "Voice",
        "kind": "wave",
        "start": 0,
        "end": 12.5,
        "channels": 1
    }
]
BatchCommand finished: OK
""",
        ])

    def send(
        self,
        command: str,
        timeout: float | None = None,
    ) -> str:
        self.commands.append(command)

        if command.startswith("Help:"):
            return "BatchCommand finished: OK"

        if command.startswith("OpenProject2:"):
            return "BatchCommand finished: OK"

        if command == "GetInfo: Type=Tracks":
            return next(self.responses)

        return "BatchCommand finished: OK"


def test_pipe_creation() -> None:
    pipe = AudacityPipe(
        Path("/tmp/to"),
        Path("/tmp/from"),
    )

    assert pipe is not None
    assert pipe._reader is None
    assert pipe._writer is None


def test_default_pipe() -> None:
    pipe = AudacityPipe.default()

    assert pipe._to_pipe == PIPE_TO
    assert pipe._from_pipe == PIPE_FROM


def test_send_times_out_when_audacity_does_not_respond(
    tmp_path: Path,
) -> None:
    to_pipe = tmp_path / "to"
    from_pipe = tmp_path / "from"

    os.mkfifo(to_pipe)
    os.mkfifo(from_pipe)

    pipe = AudacityPipe(
        to_pipe,
        from_pipe,
    )

    def fake_audacity() -> None:
        with to_pipe.open("r") as reader:
            reader.readline()

        with from_pipe.open("w") as writer:
            time.sleep(1)

    thread = threading.Thread(
        target=fake_audacity,
        daemon=True,
    )
    thread.start()

    with pytest.raises(PipeTimeoutError):
        pipe.send(
            "GetInfo: Type=Tracks",
            timeout=0.1,
        )


def test_send_raises_if_pipes_are_missing(tmp_path: Path) -> None:
    to_pipe = tmp_path / "missing.to"
    from_pipe = tmp_path / "missing.from"

    pipe = AudacityPipe(
        to_pipe=to_pipe,
        from_pipe=from_pipe,
    )

    with pytest.raises(PipeConnectionError):
        pipe.send("Help:")


def test_send_writes_command_and_reads_response(
    tmp_path: Path,
) -> None:
    to_pipe = tmp_path / "to"
    from_pipe = tmp_path / "from"

    os.mkfifo(to_pipe)
    os.mkfifo(from_pipe)

    pipe = AudacityPipe(
        to_pipe=to_pipe,
        from_pipe=from_pipe,
    )

    received: list[str] = []

    def fake_audacity() -> None:
        with to_pipe.open("r") as reader:
            command = reader.readline().rstrip("\n")
            received.append(command)

        with from_pipe.open("w") as writer:
            writer.write("BatchCommand finished: OK\n")
            writer.flush()

    thread = threading.Thread(
        target=fake_audacity,
    )
    thread.start()

    response = pipe.send("Help:")

    thread.join(timeout=2.0)

    assert received == ["Help:"]
    assert response == "BatchCommand finished: OK\n"


def test_send_reads_multiline_response_until_batch_finished(
    tmp_path: Path,
) -> None:
    to_pipe = tmp_path / "to"
    from_pipe = tmp_path / "from"

    os.mkfifo(to_pipe)
    os.mkfifo(from_pipe)

    pipe = AudacityPipe(
        to_pipe=to_pipe,
        from_pipe=from_pipe,
    )

    response_lines = [
        "[\n",
        '  { "name": "Voice",\n',
        '    "start": 0,\n',
        '    "end": 12.5 }\n',
        "]\n",
        "BatchCommand finished: OK\n",
    ]

    received: list[str] = []

    def fake_audacity() -> None:
        with to_pipe.open("r") as reader:
            received.append(reader.readline().rstrip("\n"))

        with from_pipe.open("w") as writer:
            for line in response_lines:
                writer.write(line)
                writer.flush()

    thread = threading.Thread(
        target=fake_audacity,
    )
    thread.start()

    response = pipe.send("GetInfo: Type=Tracks")

    thread.join(timeout=2.0)

    assert received == ["GetInfo: Type=Tracks"]
    assert response == "".join(response_lines)


def test_send_times_out_without_response(
    tmp_path: Path,
) -> None:
    to_pipe = tmp_path / "to"
    from_pipe = tmp_path / "from"

    to_pipe.touch()
    from_pipe.touch()

    pipe = AudacityPipe(
        to_pipe=to_pipe,
        from_pipe=from_pipe,
    )

    with patch(
        "audacity_project_tools.pipe.select.select",
        return_value=([], [], []),
    ):
        with pytest.raises(PipeTimeoutError):
            pipe.send(
                "Exit:",
                timeout=0.1,
            )


def test_send_returns_failed_response(
    tmp_path: Path,
) -> None:
    to_pipe = tmp_path / "to"
    from_pipe = tmp_path / "from"

    os.mkfifo(to_pipe)
    os.mkfifo(from_pipe)

    pipe = AudacityPipe(
        to_pipe=to_pipe,
        from_pipe=from_pipe,
    )

    def fake_audacity() -> None:
        with to_pipe.open("r") as reader:
            reader.readline()

        with from_pipe.open("w") as writer:
            writer.write("BatchCommand finished: Failed!\n")
            writer.flush()

    thread = threading.Thread(
        target=fake_audacity,
    )
    thread.start()

    response = pipe.send("SomeCommand:")

    thread.join(timeout=2.0)

    assert response == "BatchCommand finished: Failed!\n"
