from __future__ import annotations

import os
from pathlib import Path
from typing import TextIO

from .exceptions import PipeConnectionError


PIPE_TO = Path("/tmp") / f"audacity_script_pipe.to.{os.getuid()}"
PIPE_FROM = Path("/tmp") / f"audacity_script_pipe.from.{os.getuid()}"

class AudacityPipe:
    """Low-level communication with Audacity through mod-script-pipe."""

    def __init__(
        self,
        to_pipe: Path,
        from_pipe: Path,
    ) -> None:
        self._to_pipe = to_pipe
        self._from_pipe = from_pipe

        self._writer: TextIO | None = None
        self._reader: TextIO | None = None

    @classmethod
    def default(cls) -> AudacityPipe:
        return cls(PIPE_TO, PIPE_FROM)

    def connect(self) -> None:
        """Open the communication pipes to Audacity."""
        self._writer = self._to_pipe.open("w")
        self._reader = self._from_pipe.open("r")

    def send(self, command: str) -> str:
        """Send a command and return Audacity response."""

        if self._writer is None or self._reader is None:
            raise PipeConnectionError("Pipe is not connected.")

        self._writer.write(command)
        self._writer.write("\n")
        self._writer.flush()

        lines: list[str] = []

        while True:
            line = self._reader.readline()

            if not line:
                break

            lines.append(line)

            if line.startswith("BatchCommand finished:"):
                break

        return "".join(lines)

    def close(self) -> None:
        """Close communication channels."""

        if self._writer is not None:
            self._writer.close()
            self._writer = None

        if self._reader is not None:
            self._reader.close()
            self._reader = None

    def __enter__(self) -> "AudacityPipe":
        self.connect()
        return self


    def __exit__(
        self,
        exc_type,
        exc,
        tb,
    ) -> None:
        self.close()


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
