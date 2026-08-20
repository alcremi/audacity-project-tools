from pathlib import Path

from audacity_project_tools import Track, Project, ConversionReport, ConversionFailure


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


def test_project_tracks_are_independent() -> None:
    project1 = Project(path=Path("one.aup"))
    project2 = Project(path=Path("two.aup"))

    track = Track(
        name="Voice",
        start=0.0,
        end=12.5,
        channels=1,
    )

    project1.tracks.append(track)

    assert project1.tracks == [track]
    assert project2.tracks == []


def test_conversion_reports_failures_are_independent() -> None:
    report1 = ConversionReport()
    report2 = ConversionReport()

    failure = ConversionFailure(
        source=Path("project.aup"),
        reason="Missing data directory",
    )

    report1.failures.append(failure)

    assert report1.failures == [failure]
    assert report2.failures == []
