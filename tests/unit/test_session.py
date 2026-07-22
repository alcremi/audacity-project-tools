from pathlib import Path


from audacity_project_tools import AudacityClient
from audacity_project_tools import AudacitySession


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


class FakeClient2:
    def __init__(self) -> None:
        self.exited = False

    def exit_audacity(self) -> None:
        self.exited = True


def test_session_close_exits_audacity() -> None:
    process = FakeProcess2()

    session = AudacitySession(process=process)

    client = FakeClient2()
    session._client = client

    session.close()

    assert client.exited
    assert process.waited
