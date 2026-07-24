import sys
from pathlib     import Path

from .client     import AudacityClient
from .converter  import ProjectConverter
from .cli        import parse_args
from .exceptions import PipeConnectionError, DirectoryNotFoundError
from .api        import convert_directory


def run() -> int:
    args = parse_args()

    if not args.directory.is_dir():
        print(
            f"Error: '{args.directory}' is not a directory.",
            file=sys.stderr,
        )
        return 1

    count = convert_directory(
        args.directory,
        dry_run=args.dry_run,
    )

    print(f"Processed {count} project(s).")

    return 0


def main() -> int:
    print("Entree dans 'main()'")
    try:
        return run()
    except PipeConnectionError:
        print("Error: Audacity is not running.", file=sys.stderr)
        return 1
    except DirectoryNotFoundError: # Not implemented yet
        print("Error: Directory '/tmp/foo' does not exist.", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
