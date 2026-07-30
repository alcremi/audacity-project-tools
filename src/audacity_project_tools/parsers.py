from __future__ import annotations

import json

from .models import Track


def parse_tracks(response: str) -> list[Track]:

    data = json.loads(response)

    tracks = []

    for item in data:

        if item.get("kind") != "wave":
            continue

        tracks.append(
            Track(
                name=item["name"],
                start=item["start"],
                end=item["end"],
                channels=item["channels"],
            )
        )

    return tracks
