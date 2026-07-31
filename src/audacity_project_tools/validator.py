from __future__ import annotations

from pathlib import Path

from .models import ValidationResult, ConversionDecision


def should_convert(source: Path) -> ValidationResult:
    """Determine whether a project should be converted."""

    destination = source.with_suffix(".aup3")

    if destination.exists():
        return ValidationResult(
            decision=ConversionDecision.SKIP_ALREADY_CONVERTED,
            message="Project already converted.",
        )

    data_directory = source.with_name(f"{source.stem}_data")

    if not data_directory.is_dir():
        return ValidationResult(
            decision=ConversionDecision.FAIL_MISSING_DATA,
            message=f"Missing data directory: {data_directory.name}",
        )

    return ValidationResult(
        decision=ConversionDecision.CONVERT,
    )
