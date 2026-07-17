from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Track:
    """Audio track information returned by Audacity."""

    name: str
    start: float
    end: float
    channels: int

@dataclass(slots=True)
class Project:
    """An Audacity project."""

    path: Path
