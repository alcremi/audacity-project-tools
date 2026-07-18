import sys
from pathlib import Path

from .client import AudacityClient
from .converter import ProjectConverter
from .scanner import ProjectScanner
from .connection import connect


def convert_directory(
        root: Path,
        converter: ProjectConverter,
        scanner: ProjectScanner,
) -> None:
    for source in scanner.scan(root):
        converter.convert(
            source,
            source.with_suffix(".aup3"),
        )

def main() -> int:
    root = Path(sys.argv[1])

    pipe = connect()
    client = AudacityClient(pipe)
    converter = ProjectConverter(client)
    scanner = ProjectScanner()

    convert_directory(root, converter, scanner)

    client.exit_project()
    return 0
