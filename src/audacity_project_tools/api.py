from pathlib import Path
from dataclasses import dataclass, field
import logging

from .converter import ProjectConverter
from .scanner   import ProjectScanner
from .session   import AudacitySession
from .models    import ConversionDecision
from .validator import should_convert

logger = logging.getLogger(__name__)

@dataclass
class ConversionFailure:
    source: Path
    reason: str

@dataclass
class ConversionReport:
    count: int
    converted: int
    skipped : int
    failed: int
    failures: list[ConversionFailure]


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

    if dry_run:
        for source in projects:
            decision = should_convert(source)

            match decision.decision:
                case ConversionDecision.CONVERT:
                    count += 1
                    print(f"{source} -> {source.with_suffix('.aup3')}")
                    continue
                case ConversionDecision.SKIP_ALREADY_CONVERTED:
                    skipped += 1
                    continue
                case ConversionDecision.FAIL_MISSING_DATA:
                    failed += 1
                    continue

        return ConversionReport(count=count, converted=0, skipped=skipped, failed=failed, failures=[])


    failures: list[ConversionFailure] = []

    for source in projects:
        decision = should_convert(source)
        match decision.decision:
            case ConversionDecision.CONVERT:
                session = AudacitySession()
                count += 1

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
                continue
            case ConversionDecision.SKIP_ALREADY_CONVERTED:
                skipped += 1
                continue
            case ConversionDecision.FAIL_MISSING_DATA:
                failed += 1
                continue

    return ConversionReport(count=count, converted=converted, skipped=skipped, failed=failed, failures=failures)
