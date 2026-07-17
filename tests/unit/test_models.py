from pathlib import Path

from audacity_project_tools import Track
from audacity_project_tools import Project


def test_track_creation() -> None:
    track = Track(
        name="Voice",
        start=0.0,
        end=12.5,
        channels=1,
    )

    assert track.name == "Voice"
    assert track.end == 12.5

def test_project_creation() -> None:
    project = Project(
        path=Path("/huge/Douchet/AudioCinema/Audio/Losey_Cntq19950105_c.aup")
    )

    assert project.path == Path("/huge/Douchet/AudioCinema/Audio/Losey_Cntq19950105_c.aup")
