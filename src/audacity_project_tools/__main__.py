import sys
from pathlib     import Path

from .client     import AudacityClient
from .converter  import ProjectConverter
from .scanner    import ProjectScanner
from .connection import connect
from .cli        import parse_args
from .exceptions import PipeConnectionError, DirectoryNotFoundError


def convert_directory(
        root: Path,
        converter: ProjectConverter,
        scanner: ProjectScanner,
        flagDryRun: bool,
) -> int:
    print(f"Scanning {root}...")

    projects = list(scanner.scan(root))

    count = len(projects)
    print(f"Found {count} project{'s' if count != 1 else ''}.")
    if not projects:
        return 0

    if flagDryRun:
        print("Would convert:")
    else:
        print("Converting")
    nb: int = 0
    for source in scanner.scan(root):
        ++nb
        destination = source.with_suffix(".aup3")

        if flagDryRun:
            print(f"   {source} -> {destination}")
            continue

        print(f"   {source.name}")
        converter.convert(source, destination)

    return nb


def run() -> int:
    args = parse_args()
    root = args.directory
    flagDryRun = args.dry_run

    if not root.is_dir():
        print(f"Error: '{root}' is not a directory.", file=sys.stderr)
        return 1

    pipe = connect()
    client = AudacityClient(pipe)
    converter = ProjectConverter(client)
    scanner = ProjectScanner()

    nb = convert_directory(root, converter, scanner, flagDryRun)

    client.exit_project()
    print("Done.")
    return 0

def main() -> int:
    try:
        return run()
    except PipeConnectionError:
        print("Error: Audacity is not running.", file=sys.stderr)
        return 1
    except DirectoryNotFoundError: # Not implemented yet
        print("Error: Directory '/tmp/foo' does not exist.", file=sys.stderr)
        return 1
