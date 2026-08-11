from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
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

class ConversionDecision(Enum):
    CONVERT = auto()
    SKIP_ALREADY_CONVERTED = auto()
    FAIL_MISSING_DATA = auto()

@dataclass(frozen=True, slots=True)
class ValidationResult:
    decision: ConversionDecision
    message: str | None = None

@dataclass
class ConversionFailure:
    source: Path
    reason: str

@dataclass(slots=True)
class ConversionReport:
    count: int = 0
    converted: int = 0
    skipped: int = 0
    failed: int = 0
    failures: list[ConversionFailure] = field(default_factory=list)

class ConversionMode(Enum):
    AUP_TO_AUP3 = "aup-to-aup3"
    AUP3_TO_AUP3 = "aup3-to-aup3"
