from pathlib import Path

from audacity_project_tools import AudacityPipe
from audacity_project_tools import AudacityClient
from audacity_project_tools import FakePipe3, FakePipe4


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



def test_open_project() -> None:

    pipe = FakePipe4()
    client = AudacityClient(pipe)

    client.open_project(Path("/tmp/test.aup"))

    assert pipe.commands == [
        'OpenProject2: Filename="/tmp/test.aup"',
        "GetInfo: Type=Tracks",
        "GetInfo: Type=Tracks",
        "GetInfo: Type=Tracks",
    ]

def test_save_project() -> None:

    pipe = FakePipe3()
    client = AudacityClient(pipe)

    client.save_project(Path("/tmp/output.aup3"))

    assert pipe.commands[-1] == (
        'SaveProject2: Filename="/tmp/output.aup3"'
    )

def test_exit_audacity() -> None:

    pipe = FakePipe3()
    client = AudacityClient(pipe)

    client.exit_audacity()

    assert pipe.commands[-1] == (
        'Exit:'
    )

def test_load_project() -> None:

    pipe = FakePipe3()
    client = AudacityClient(pipe)

    project = client.load_project(Path("/tmp/test.aup"))

    assert project.path == Path("/tmp/test.aup")
    assert len(project.tracks) == 1
    assert project.tracks[0].name == "Voice"
