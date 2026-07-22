from pathlib import Path

from .converter import ProjectConverter
from .session import AudacitySession


def convert(source: Path, destination: Path) -> None:
    """Convert an Audacity project."""

    session = AudacitySession()

    try:
        client = session.start()

        converter = ProjectConverter(client)
        converter.convert(source, destination)

    finally:
        session.close()
