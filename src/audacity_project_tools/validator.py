from __future__ import annotations

from pathlib import Path

from .models import ValidationResult, ConversionDecision


def should_convert(
    source: Path,
    destination: Path,
) -> ValidationResult:

    data_dir = source.with_name(
        source.stem + "_data"
    )

    if not data_dir.is_dir():
        return ValidationResult(
            decision=ConversionDecision.FAIL_MISSING_DATA,
            message=f"Missing data directory: {data_dir.name}",
        )

    if destination.exists():
        return ValidationResult(
            decision=ConversionDecision.SKIP_ALREADY_CONVERTED,
            message=f"Already converted: {destination.name}",
        )

    return ValidationResult(
        decision=ConversionDecision.CONVERT,
    )
