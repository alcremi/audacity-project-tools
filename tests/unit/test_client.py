from pathlib import Path

from audacity_project_tools import AudacityPipe
from audacity_project_tools import AudacityClient


def test_client() -> None:
    pipe = FakePipe()
    client = AudacityClient(pipe)
    client.help()
    assert pipe.command == "Help:"



class FakePipe:
    def __init__(self) -> None:
        self.command = ""

    def send(self, command: str) -> str:
        self.command = command
        return "BatchCommand finished: OK"


def test_help_command() -> None:
    pipe = FakePipe()
    client = AudacityClient(pipe)

    client.help()

    assert pipe.command == "Help:"


class FakePipe2:
    def __init__(self) -> None:
        self.command = ""

    def send(self, command: str) -> str:
        self.command = command
        return """
[
    {
        "name": "Voice",
        "start": 0,
        "end": 12.5,
        "channels": 1
    }
]
"""

def test_get_tracks_command() -> None:
    pipe = FakePipe2()
    client = AudacityClient(pipe)

    tracks = client.get_tracks()

    assert pipe.command == "GetInfo: Type=Tracks"
    assert len(tracks) == 1


class FakePipe3:
    def __init__(self) -> None:
        self.command = ""
        self.commands = []

    def send(self, command: str) -> str:
        self.command = command
        self.commands.append(command)
        return "BatchCommand finished: OK"

def test_open_project() -> None:

    pipe = FakePipe3()
    client = AudacityClient(pipe)

    client.open_project(Path("/tmp/test.aup"))

    assert pipe.command == 'OpenProject2: Filename="/tmp/test.aup"'

def test_save_project() -> None:

    pipe = FakePipe3()
    client = AudacityClient(pipe)

    client.save_project(Path("/tmp/output.aup3"))

    assert pipe.commands[-1] == (
        'SaveProject2: Filename="/tmp/output.aup3"'
    )

def test_exit_project() -> None:

    pipe = FakePipe3()
    client = AudacityClient(pipe)

    client.exit_project()

    assert pipe.commands[-1] == (
        'Exit:"'
    )
