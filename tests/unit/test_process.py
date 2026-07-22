from unittest.mock import patch

from pathlib import Path

from audacity_project_tools.process import AudacityProcess


def test_start() -> None:
    with patch("subprocess.Popen") as popen:
        process = AudacityProcess()

        process.start()

        popen.assert_called_once_with(
            ["audacity"],
            text=True,
        )


class FakeProcess:
    def __init__(self) -> None:
        self.timeout: float | None = None

    def wait(self, timeout: float | None = None) -> None:
        self.timeout = timeout

def test_wait_for_exit() -> None:
    process = AudacityProcess()
    process._process = FakeProcess()

    process.wait_for_exit()

    assert process._process.timeout == 5.0


import subprocess

class FakeProcessTimeout:
    def wait(self, timeout: float | None = None) -> None:
        raise subprocess.TimeoutExpired(
            cmd="audacity",
            timeout=timeout,
        )

import pytest

from audacity_project_tools.exceptions import AudacityProcessError


def test_wait_for_exit_timeout() -> None:
    process = AudacityProcess()
    process._process = FakeProcessTimeout()

    with pytest.raises(AudacityProcessError):
        process.wait_for_exit()
