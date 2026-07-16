from pathlib import Path

from audacity_project_tools import AudacityPipe
from audacity_project_tools import AudacityClient
# from audacity_project_tools import FakePipe

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
