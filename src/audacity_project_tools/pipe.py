from __future__ import annotations

from pathlib import Path

from .exceptions import PipeConnectionError


class AudacityPipe:
    """Low-level communication with Audacity through mod-script-pipe."""

    def __init__(
        self,
        to_pipe: Path,
        from_pipe: Path,
    ) -> None:
        self._to_pipe = to_pipe
        self._from_pipe = from_pipe

    def connect(self) -> None:
        """Open communication channels with Audacity."""
        raise NotImplementedError

    def send(self, command: str) -> str:
        """Send a command and return Audacity response."""
        raise NotImplementedError

    def close(self) -> None:
        """Close communication channels."""
        raise NotImplementedError
