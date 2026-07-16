from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Track:
    """Audio track information returned by Audacity."""

    name: str
    start: float
    end: float
    channels: int
