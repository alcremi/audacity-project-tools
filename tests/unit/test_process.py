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


class FakeProcessTimeout:
    def __init__(self) -> None:
        self.timeout: float | None = None
        self.pid = 0

    def poll(self) -> None:
        return None

    def wait(self, timeout: float | None = None) -> None:
        raise subprocess.TimeoutExpired(
            cmd="audacity",
            timeout=timeout,
        )


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


def test_wait_for_exit_cleans_up_pipes_after_kill(
    tmp_path: Path,
) -> None:
    process = AudacityProcess(
        pipe_to=tmp_path / "to",
        pipe_from=tmp_path / "from",
    )

    process._pipe_to.touch()
    process._pipe_from.touch()

    fake = FakeProcess3(
        exit_on_wait=False,
        terminate_works=False,
    )

    process._process = fake

    process.wait_for_exit()

    assert fake.killed
    assert not process._pipe_to.exists()
    assert not process._pipe_from.exists()


def test_cleanup_debug_reports(tmp_path: Path) -> None:
    process = AudacityProcess()

    fake = FakeProcess3()
    process._process = fake

    report1 = tmp_path / f"Audacity_dbgrpt-{fake.pid}-001"
    report2 = tmp_path / f"Audacity_dbgrpt-{fake.pid}-002"

    report1.mkdir()
    report2.mkdir()

    with patch.object(
        Path,
        "glob",
        return_value=[report1, report2],
    ) as mock_glob:
        with patch(
            "audacity_project_tools.process.shutil.rmtree"
        ) as mock_rmtree:
            process.cleanup_debug_reports()

    mock_glob.assert_called_once_with(
        f"Audacity_dbgrpt-{fake.pid}-*"
    )

    assert mock_rmtree.call_count == 2
    mock_rmtree.assert_any_call(report1)
    mock_rmtree.assert_any_call(report2)


def test_wait_for_exit_calls_debug_report_cleanup_after_kill() -> None:
    process = AudacityProcess()

    fake = FakeProcess3(
        exit_on_wait=False,
        terminate_works=False,
    )

    process._process = fake

    with patch.object(
        process,
        "cleanup_debug_reports",
    ) as cleanup:
        process.wait_for_exit()

    assert fake.killed
    cleanup.assert_called_once()


def test_wait_until_ready() -> None:
    process = AudacityProcess()

    with patch.object(Path, "exists", return_value=True):
        process.wait_until_ready()


def test_wait_until_ready_timeout() -> None:
    process = AudacityProcess()

    times = iter([0.0, 31.0])

    with patch.object(
        Path,
        "exists",
        return_value=False,
    ):
        with patch(
            "audacity_project_tools.process.time.monotonic",
            side_effect=lambda: next(times),
        ):
            with pytest.raises(AudacityProcessError):
                process.wait_until_ready()


def test_start_cleans_up_old_pipes() -> None:
    process = AudacityProcess()

    with patch.object(
        process,
        "cleanup_pipes",
    ) as cleanup:
        with patch(
            "subprocess.Popen",
        ):
            process.start()

    cleanup.assert_called_once()


def test_start_propagates_popen_error() -> None:
    process = AudacityProcess()

    error = OSError("audacity not found")

    with patch(
        "subprocess.Popen",
        side_effect=error,
    ):
        with pytest.raises(OSError, match="audacity not found"):
            process.start()


def test_start_stores_process() -> None:
    process = AudacityProcess()

    fake = FakeProcess3()

    with patch(
        "subprocess.Popen",
        return_value=fake,
    ):
        process.start()

    assert process._process is fake


def test_wait_until_ready_fails_if_process_exited() -> None:
    process = AudacityProcess()

    fake = FakeProcess3()
    process._process = fake

    with patch.object(
        Path,
        "exists",
        return_value=False,
    ):
        with patch.object(
            fake,
            "poll",
            return_value=1,
        ):
            with pytest.raises(
                AudacityProcessError,
                match="Audacity exited",
            ):
                process.wait_until_ready()


def test_wait_until_ready_detects_process_exit_during_wait() -> None:
    process = AudacityProcess()

    fake = FakeProcess3()
    process._process = fake

    poll_results = iter([None, 1])

    with patch.object(
        Path,
        "exists",
        return_value=False,
    ):
        with patch.object(
            fake,
            "poll",
            side_effect=lambda: next(poll_results),
        ):
            with patch(
                "audacity_project_tools.process.time.sleep",
            ):
                with pytest.raises(
                    AudacityProcessError,
                    match="Audacity exited",
                ):
                    process.wait_until_ready()


def test_cleanup_pipes_removes_existing_pipes(tmp_path: Path) -> None:
    pipe_to = tmp_path / "audacity.to"
    pipe_from = tmp_path / "audacity.from"

    pipe_to.touch()
    pipe_from.touch()

    process = AudacityProcess(
        pipe_to=pipe_to,
        pipe_from=pipe_from,
    )

    process.cleanup_pipes()

    assert not pipe_to.exists()
    assert not pipe_from.exists()


def test_cleanup_pipes_ignores_missing_pipes(tmp_path: Path) -> None:
    pipe_to = tmp_path / "audacity.to"
    pipe_from = tmp_path / "audacity.from"

    process = AudacityProcess(
        pipe_to=pipe_to,
        pipe_from=pipe_from,
    )

    process.cleanup_pipes()

    assert not pipe_to.exists()
    assert not pipe_from.exists()


def test_wait_for_exit_cleans_up_after_terminate() -> None:
    process = AudacityProcess()

    fake = FakeProcess3(
        exit_on_wait=False,
        terminate_works=True,
    )
    process._process = fake

    with patch.object(
        process,
        "cleanup_pipes",
    ) as cleanup_pipes:
        with patch.object(
            process,
            "cleanup_debug_reports",
        ) as cleanup_debug_reports:
            process.wait_for_exit()

    cleanup_pipes.assert_called_once()
    cleanup_debug_reports.assert_called_once()


def test_wait_for_exit_cleans_up_after_kill() -> None:
    process = AudacityProcess()

    fake = FakeProcess3(
        exit_on_wait=False,
        terminate_works=False,
    )
    process._process = fake

    with patch.object(
        process,
        "cleanup_pipes",
    ) as cleanup_pipes:
        with patch.object(
            process,
            "cleanup_debug_reports",
        ) as cleanup_debug_reports:
            process.wait_for_exit()

    cleanup_pipes.assert_called_once()
    cleanup_debug_reports.assert_called_once()


def test_wait_for_exit_without_process() -> None:
    process = AudacityProcess()

    process.wait_for_exit()
