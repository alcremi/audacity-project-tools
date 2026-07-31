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
        validation = should_convert(source)
        count += 1

        match validation.decision:
            case ConversionDecision.CONVERT:
                if dry_run:
                    print(f"{source} -> {source.with_suffix('.aup3')}")
                else:
                    session = AudacitySession()

                    try:
                        client = session.start()
                        converter = ProjectConverter(client)

                        destination = source.with_suffix(".aup3")
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
