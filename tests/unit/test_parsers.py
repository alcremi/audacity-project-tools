from audacity_project_tools.models import Track
from audacity_project_tools.parsers import parse_tracks


def test_parse_tracks() -> None:
    response = """
    [
        {
            "name": "Voice",
            "kind": "wave",
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

def test_parse_tracks_ignores_label_tracks():
    response = """
    [
        {
            "name": "Voice",
            "kind": "wave",
            "start": 0,
            "end": 12.5,
            "channels": 1
        },
        {
            "name": "Labels",
            "kind": "label"
        }
    ]
    """

    tracks = parse_tracks(response)

    assert len(tracks) == 1
    assert tracks[0].name == "Voice"

def test_parse_tracks_with_only_labels() -> None:
    response = """
    [
        {
            "name": "Markers",
            "kind": "label"
        }
    ]
    """

    tracks = parse_tracks(response)

    assert tracks == []
