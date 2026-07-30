from pathlib import Path
from dataclasses import dataclass, field
import logging

from .converter import ProjectConverter
from .scanner   import ProjectScanner
from .session   import AudacitySession

logger = logging.getLogger(__name__)

@dataclass
class ConversionFailure:
    source: Path
    reason: str

@dataclass
class ConversionReport:
    count: int
    converted: int
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

    if dry_run:
        count = 0
        for source in projects:
            print(f"{source} -> {source.with_suffix('.aup3')}")
            count += 1
        return ConversionReport(count=count, converted=0, failed=0, failures=[])


    count = 0
    converted = 0
    failed = 0
    failures: list[ConversionFailure] = []

    for source in projects:
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

    return ConversionReport(count=count, converted=converted, failed=failed, failures=failures)
