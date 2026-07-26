from __future__ import annotations

import os
import subprocess
import signal
import time
import shutil
from pathlib import Path

from .pipe       import PIPE_TO, PIPE_FROM
from .exceptions import AudacityProcessError


class AudacityProcess:
    """Manage the Audacity application process."""

    def __init__(
        self,
        executable: str = "audacity",
        #executable: str = "/huge/Telechargements/audacity-linux-3.7.8-x64-22.04.AppImage",
        pipe_to: Path = PIPE_TO,
        pipe_from: Path = PIPE_FROM,
    ) -> None:
        self._executable = executable
        self._pipe_to = pipe_to
        self._pipe_from = pipe_from
        self._process: subprocess.Popen[str] | None = None

    def cleanup_pipes(self) -> None:
        for pipe in (self._pipe_to, self._pipe_from):
            if pipe.exists():
                pipe.unlink()

    def start(self) -> None:
        """Start Audacity."""

        self.cleanup_pipes()

        self._process = subprocess.Popen(
            [self._executable],
            text=True,
        )
        print(f"Audacity PID: {self._process.pid}")

    def wait_until_ready(self) -> None:
        """Wait until Audacity scripting pipe is available."""


        timeout = 30.0
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            if self._pipe_to.exists() and self._pipe_from.exists():
                print("On a detecte les 2 pipes")
                return

            time.sleep(0.1)

        print("Sortie de boucle")
        raise AudacityProcessError(
            "Timed out while waiting for Audacity pipes."
        )

    def cleanup_debug_reports_old(self) -> None:
        """Remove Audacity debug report directories."""

        tmp = Path("/tmp")

        for path in tmp.glob("Audacity_dbgrpt-*"):
            if path.is_dir():
                shutil.rmtree(path)

    def cleanup_debug_reports(self) -> None:
        """Remove Audacity debug report directories."""
        if self._process is None:
            return

        pattern = f"Audacity_dbgrpt-{self._process.pid}-*"

        for path in Path("/tmp").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)

    def wait_for_exit(self, timeout: float = 5.0) -> None:
        """Wait for Audacity to terminate, forcing termination if needed."""

        if self._process is None:
            return

        try:
            self._process.wait(timeout=timeout)

        except subprocess.TimeoutExpired:
            print("Audacity did not exit normally.")

            self._process.terminate()

            try:
                self._process.wait(timeout=timeout)

            except subprocess.TimeoutExpired:
                print("Audacity ignored SIGTERM, killing process.")
                self._process.kill()
                self._process.wait()

            finally:
                self.cleanup_pipes()
                self.cleanup_debug_reports()
