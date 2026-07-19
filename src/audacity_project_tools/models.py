from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True, frozen=True)
class Track:
    """A track in an Audacity project."""

    name: str
    start: float
    end: float
    channels: int

@dataclass(slots=True)
class Project:
    """An Audacity project loaded from disk."""

    path: Path
    tracks: list[Track] = field(default_factory=list)
