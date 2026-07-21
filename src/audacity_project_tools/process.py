from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from .pipe import PIPE_TO, PIPE_FROM
from .exceptions import AudacityProcessError


class AudacityProcess:
    """Manage the Audacity application process."""

    def __init__(
        self,
        executable: str = "audacity",
        pipe_to: Path = PIPE_TO,
        pipe_from: Path = PIPE_FROM,
    ) -> None:
        self._executable = executable
        self._pipe_to = pipe_to
        self._pipe_from = pipe_from
        self._process: subprocess.Popen[str] | None = None

    def start(self) -> None:
        """Start Audacity."""

        self._process = subprocess.Popen(
            [self._executable],
            text=True,
        )

    def wait_until_ready(self) -> None:
        """Wait until Audacity scripting pipe is available."""


        timeout = 10.0
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            if self._pipe_to.exists() and self._pipe_from.exists():
                return

            time.sleep(0.1)

            raise AudacityProcessError(
                "Timed out while waiting for Audacity pipes."
            )
