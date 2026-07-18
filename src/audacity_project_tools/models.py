from __future__ import annotations

from dataclasses import dataclass, field
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
    tracks: list[Track] = field(default_factory=list)

"""
    def save(
            self,
            client: AudacityClient,
            path: Path,
    ) -> None:
        client.save_project(path)
"""
