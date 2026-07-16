from audacity_project_tools.models import Track
from audacity_project_tools.parsers import parse_tracks


def test_parse_tracks() -> None:
    response = """
    [
        {
            "name": "Voice",
            "start": 0,
            "end": 12.5,
            "channels": 1
        }
    ]
    """

    tracks = parse_tracks(response)

    assert len(tracks) == 1

    track = tracks[0]

    assert isinstance(track, Track)
    assert track.name == "Voice"
    assert track.start == 0
    assert track.end == 12.5
    assert track.channels == 1
