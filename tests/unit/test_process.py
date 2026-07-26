import subprocess
import pytest

from unittest.mock import patch

from pathlib import Path

from audacity_project_tools.process import AudacityProcess
from audacity_project_tools.exceptions import AudacityProcessError


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
        self.pid = 0

    def wait(self, timeout: float | None = None) -> None:
        self.timeout = timeout

    def poll(self) -> None:
        return None

def _test_wait_for_exit() -> None:
    process = AudacityProcess()
    process._process = FakeProcess()

    process.wait_for_exit()

    assert process._process.timeout == 5.0


class FakeProcessTimeout:
    def __init__(self) -> None:
        self.timeout: float | None = None
        self.pid = 0

    def wait(self, timeout: float | None = None) -> None:
        self.timeout = timeout

    def poll(self) -> None:
        return None

    def wait(self, timeout: float | None = None) -> None:
        raise subprocess.TimeoutExpired(
            cmd="audacity",
            timeout=timeout,
        )

def _test_wait_for_exit_timeout() -> None:
    process = AudacityProcess()
    process._process = FakeProcessTimeout()

    with pytest.raises(AudacityProcessError):
        process.wait_for_exit()


class FakeProcess3:
    def __init__(
        self,
        *,
        exit_on_wait: bool = True,
        terminate_works: bool = True,
    ) -> None:
        self.pid = 12345

        self.exit_on_wait = exit_on_wait
        self.terminate_works = terminate_works

        self.terminated = False
        self.killed = False
        self.wait_calls = 0

    def wait(self, timeout: float | None = None) -> None:
        self.wait_calls += 1

        if self.wait_calls == 1 and not self.exit_on_wait:
            raise subprocess.TimeoutExpired(
                cmd="audacity",
                timeout=timeout,
            )

        if self.wait_calls == 2 and self.terminated:
            if self.terminate_works:
                return

            raise subprocess.TimeoutExpired(
                cmd="audacity",
                timeout=timeout,
            )

    def poll(self) -> int | None:
        if self.killed:
            return 0

        if self.terminated and self.terminate_works:
            return 0

        return None

    def terminate(self) -> None:
        self.terminated = True

    def kill(self) -> None:
        self.killed = True

def test_wait_for_exit_normal() -> None:
    """ 1) Fermeture normale """
    process = AudacityProcess()

    fake = FakeProcess3()

    process._process = fake

    process.wait_for_exit()

    assert fake.wait_calls == 1
    assert not fake.terminated
    assert not fake.killed

def test_wait_for_exit_timeout_terminates() -> None:
    """ 2) Timeout puis SIGTERM efficace """
    process = AudacityProcess()

    fake = FakeProcess3(
        exit_on_wait=False,
        terminate_works=True,
    )

    process._process = fake

    process.wait_for_exit()

    assert fake.terminated
    assert not fake.killed

def test_wait_for_exit_kills_if_terminate_fails() -> None:
    """ 3) SIGTERM insuffisant puis SIGKILL """
    process = AudacityProcess()

    fake = FakeProcess3(
        exit_on_wait=False,
        terminate_works=False,
    )

    process._process = fake

    process.wait_for_exit()

    assert fake.terminated
    assert fake.killed
