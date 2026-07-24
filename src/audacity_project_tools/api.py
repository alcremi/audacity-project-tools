from pathlib import Path

from .converter import ProjectConverter
from .scanner   import ProjectScanner
from .session   import AudacitySession


def convert(source: Path, destination: Path) -> None:
    """Convert an Audacity project."""

    session = AudacitySession()

    try:
        client = session.start()

        converter = ProjectConverter(client)
        converter.convert(source, destination)

    finally:
        session.close()


def convert_directory(
    root: Path,
    dry_run: bool = False,
) -> int:
    """Convert all Audacity projects found in a directory."""

    scanner = ProjectScanner()
    projects = scanner.scan(root)

    if dry_run:
        count = 0
        for source in projects:
            print(f"{source} -> {source.with_suffix('.aup3')}")
            count += 1
        return count

    session = AudacitySession()

    count = 0

    try:
        client = session.start()
        converter = ProjectConverter(client)

        for source in projects:
            destination = source.with_suffix(".aup3")
            converter.convert(source, destination)
            count += 1

    finally:
        session.close()

    return count
