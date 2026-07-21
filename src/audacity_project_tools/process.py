from __future__ import annotations

import subprocess
from pathlib import Path


class AudacityProcess:
    """Manage the Audacity application process."""

    def __init__(self, executable: str = "audacity") -> None:
        self._executable = executable
        self._process: subprocess.Popen[str] | None = None

    def start(self) -> None:
        """Start Audacity."""

        self._process = subprocess.Popen(
            [self._executable],
            text=True,
        )
