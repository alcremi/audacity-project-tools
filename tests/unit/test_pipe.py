from pathlib import Path

from audacity_project_tools.pipe import AudacityPipe, PIPE_TO, PIPE_FROM


class FakePipe:
    def __init__(self) -> None:
        self.command = "Help:"

    def _sendHelp(self, command: str) -> str:
        self.command = command
        return "BatchCommand finished: OK"

    def send(self, command: str) -> str:
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

    def send(self, command: str) -> str:
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

    def send(self, command: str) -> str:
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
