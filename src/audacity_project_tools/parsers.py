from __future__ import annotations

import json

from .models import Track


def parse_tracks(response: str) -> list[Track]:
    data = json.loads(response)

    return [
        Track(
            name=item["name"],
            start=item["start"],
            end=item["end"],
            channels=item["channels"],
        )
        for item in data
    ]
