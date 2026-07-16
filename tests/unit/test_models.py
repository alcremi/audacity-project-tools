from pathlib import Path

from audacity_project_tools import Track


def test_track_creation() -> None:
    track = Track(
        name="Voice",
        start=0.0,
        end=12.5,
        channels=1,
    )

    assert track.name == "Voice"
    assert track.end == 12.5
