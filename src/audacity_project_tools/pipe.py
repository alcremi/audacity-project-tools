from __future__ import annotations

from pathlib import Path
from typing import TextIO

from .exceptions import PipeConnectionError


# _RESPONSE_END = "BatchCommand finished:"
# if line.startswith(_RESPONSE_END):

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
