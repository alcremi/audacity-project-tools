from __future__ import annotations

import os
import logging
from pathlib import Path
from typing  import TextIO

from .exceptions import PipeConnectionError

logger = logging.getLogger(__name__)

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
        """Check communication pipes."""

        if not self._to_pipe.exists() or not self._from_pipe.exists():
            raise PipeConnectionError(
                "Audacity pipes are not available."
            )

    def send(self, command: str) -> str:
        """Send a command and return Audacity response."""

        logger.debug(">>> %s", command)

        if not self._to_pipe.exists() or not self._from_pipe.exists():
            raise PipeConnectionError("Pipe is not available.")

        with self._to_pipe.open("w") as writer:
            writer.write(command)
            writer.write("\n")
            writer.flush()

        lines: list[str] = []

        with self._from_pipe.open("r") as reader:
            while True:
                line = reader.readline()

                if not line:
                    break

                lines.append(line)

                if line.startswith("BatchCommand finished:"):
                    break

        response = "".join(lines)

        logger.debug("<<< %s", response.rstrip())

        return response

    def send_once(self, command: str) -> None:
        """Send one command using a temporary FIFO connection."""

        with self._to_pipe.open("w") as writer:
            writer.write(command)
            writer.write("\n")
            writer.flush()

    def send_no_response_test1(self, command: str) -> None:
        """Send a command and do not wait for a response."""

        with self._to_pipe.open("w") as writer:
            writer.write(command)
            writer.write("\n")
            writer.flush()

    def send_no_response(self, command: str) -> None:
        """Send a command without waiting for a response."""

        fd = os.open(self._to_pipe, os.O_WRONLY)

        try:
            os.write(fd, (command + "\n").encode())
        finally:
            os.close(fd)

    def close(self) -> None:
        """Close communication channels."""
        pass

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
