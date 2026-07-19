import sys
from pathlib     import Path

from .client     import AudacityClient
from .converter  import ProjectConverter
from .scanner    import ProjectScanner
from .connection import connect
from .cli        import parse_args


def convert_directory(
        root: Path,
        converter: ProjectConverter,
        scanner: ProjectScanner,
        flagDryRun: bool,
) -> None:
    for source in scanner.scan(root):
        destination = source.with_suffix(".aup3")

        if flagDryRun:
            print(f"{source} -> {destination}")
            continue

        converter.convert(source, destination)


def main() -> int:
    args = parse_args()
    root = args.directory
    flagDryRun = args.dry_run

    pipe = connect()
    client = AudacityClient(pipe)
    converter = ProjectConverter(client)
    scanner = ProjectScanner()

    convert_directory(root, converter, scanner, flagDryRun)

    client.exit_project()
    return 0
