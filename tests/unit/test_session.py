from pathlib import Path
import pytest

from audacity_project_tools.exceptions import PipeTimeoutError
from audacity_project_tools            import AudacityClient
from audacity_project_tools            import AudacitySession


class FakeProcess:

    def __init__(self) -> None:
        self.started = False
        self.ready = False

    def start(self) -> None:
        self.started = True

    def wait_until_ready(self) -> None:
        self.ready = True


class FakePipe:

    def __init__(self) -> None:
        self.connected = False

    def connect(self) -> None:
        self.connected = True


def test_session_start_creates_client() -> None:
    process = FakeProcess()
    pipe = FakePipe()

    session = AudacitySession(
        process=process,
        pipe=pipe,
    )

    client = session.start()

    assert isinstance(client, AudacityClient)
    assert process.started
    assert process.ready
    assert pipe.connected


class FakeProcess2:
    def __init__(self) -> None:
        self.waited = False

    def wait_for_exit(self) -> None:
        self.waited = True


class FakeClient:
    def __init__(self) -> None:
        self.exited = False

    def exit_audacity(self) -> None:
        self.exited = True


def test_session_close_exits_audacity() -> None:
    process = FakeProcess2()

    session = AudacitySession(process=process)

    client = FakeClient()
    session._client = client

    session.close()

    assert client.exited
    assert process.waited


def test_close_sends_exit_and_waits_for_process() -> None:
    class FakeProcess:
        def __init__(self) -> None:
            self.waited = False

        def start(self) -> None:
            pass

        def wait_until_ready(self) -> None:
            pass

        def wait_for_exit(self) -> None:
            self.waited = True

    class FakePipe:
        def __init__(self) -> None:
            self.commands: list[str] = []

        def connect(self) -> None:
            pass

        def send(
            self,
            command: str,
            timeout: float | None = None,
        ) -> str:
            self.commands.append(command)
            return "BatchCommand finished: OK"

    process = FakeProcess()
    pipe = FakePipe()

    session = AudacitySession(
        process=process,
        pipe=pipe,
    )

    session.start()
    session.close()

    assert pipe.commands == ["Exit:"]
    assert process.waited is True


def test_session_close_waits_for_process_if_exit_fails() -> None:
    class FakeProcess:
        def __init__(self) -> None:
            self.waited = False

        def wait_for_exit(self) -> None:
            self.waited = True

    class FakeClient:
        def exit_audacity(self) -> None:
            raise PipeTimeoutError("Exit timed out")

    process = FakeProcess()
    session = AudacitySession(process=process)
    session._client = FakeClient()

    session.close()

    assert process.waited is True


def test_session_close_without_start_does_nothing() -> None:
    process = FakeProcess2()

    session = AudacitySession(process=process)

    session.close()

    assert process.waited is False
