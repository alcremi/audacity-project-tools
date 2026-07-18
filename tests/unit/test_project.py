from pathlib import Path

from audacity_project_tools import Project
from audacity_project_tools import Track


def test_project_creation() -> None:
    project = Project(Path("/tmp/test.aup"))

    assert project.path == Path("/tmp/test.aup")
    assert project.tracks == []


def test_project_tracks() -> None:
    track = Track(
        name="Voice",
        start=0,
        end=10,
        channels=1,
    )

    project = Project(
        path=Path("/tmp/test.aup"),
        tracks=[track],
    )

    assert len(project.tracks) == 1
    assert project.tracks[0].name == "Voice"

from audacity_project_tools import AudacityClient

class FakePipe3:
    def __init__(self) -> None:
        self.command = ""
        self.commands = []

    def send(self, command: str) -> str:
        self.command = command
        self.commands.append(command)
        if command != "GetInfo: Type=Tracks":
            return "BatchCommand finished: OK"
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

def test_project_save() -> None:
    pipe = FakePipe3()
    client = AudacityClient(pipe)

    project = client.load_project(Path("/tmp/test.aup"))
    client.save_project(Path("/tmp/test.aup3"))

    assert project.path == Path("/tmp/test.aup")
