from pathlib import Path
from dataclasses import dataclass, field
import logging

from .converter import ProjectConverter
from .scanner   import ProjectScanner
from .session   import AudacitySession
from .models    import ConversionDecision, ConversionFailure, ConversionReport
from .validator import should_convert

logger = logging.getLogger(__name__)


def convert(source: Path, destination: Path) -> None:
    """Convert an Audacity project."""

    logger.debug("Conversion de %s", source)
    session = AudacitySession()

    try:
        client = session.start()

        converter = ProjectConverter(client)
        converter.convert(source, destination)

    finally:
        session.close()
    logger.debug("Conversion terminee produisant %s", destination)


def convert_directory(
    root: Path,
    output_dir: Path | None = None,
    dry_run: bool = False,
) -> ConversionReport:
    """Convert all Audacity projects found in a directory."""

    scanner = ProjectScanner()
    projects = scanner.scan(root)

    count = 0
    converted = 0
    skipped = 0
    failed = 0
    failures: list[ConversionFailure] = []

    for source in projects:
        relative = source.relative_to(root)

        if output_dir is None:
            destination = source.with_suffix(".aup3")
        else:
            destination = output_dir / relative.with_suffix(".aup3")

        validation = should_convert(source, destination)

        count += 1

        match validation.decision:
            case ConversionDecision.CONVERT:
                if dry_run:
                    print(f"{source} -> {destination}")
                    continue

                destination.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                session = AudacitySession()

                try:
                    client = session.start()
                    converter = ProjectConverter(client)
                    converter.convert(source, destination)

                except Exception as exc:
                    logger.exception("Conversion failed for %s", source)
                    failed += 1
                    failures.append(
                        ConversionFailure(
                            source=source,
                            reason=str(exc),
                        )
                    )

                else:
                    converted += 1

                finally:
                    session.close()

            case ConversionDecision.SKIP_ALREADY_CONVERTED:
                skipped += 1
            case ConversionDecision.FAIL_MISSING_DATA:
                failed += 1
                if validation.message is None:
                    reason = ""
                else:
                    reason = validation.message if validation.message else ""
                failures.append(
                    ConversionFailure(
                        source=source,
                        reason=reason,
                    )
                )

    return ConversionReport(count=count, converted=converted, skipped=skipped, failed=failed, failures=failures)


def format_report(
    report: ConversionReport,
    directory: Path,
) -> str:
    """Return a formatted conversion report."""

    lines = [
        f"Projects found : {report.count}",
        f"Converted      : {report.converted}",
        f"Skipped        : {report.skipped}",
        f"Failed         : {report.failed}",
    ]

    if report.failures:
        lines.append("")
        lines.append("Failed projects:")

        for failure in report.failures:
            relative = failure.source.relative_to(directory)

            lines.append(f"  {relative}")
            lines.append(f"      {failure.reason}")

    return "\n".join(lines)
