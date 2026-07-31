import sys
import logging
from pathlib     import Path

from .api        import convert_directory
from .client     import AudacityClient
from .converter  import ProjectConverter
from .cli        import parse_args
from .exceptions import PipeConnectionError, DirectoryNotFoundError
from .models     import ConversionFailure, ConversionReport


logging.basicConfig(
    filename="audacity-project-tools.log",
    #level=logging.INFO,
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
)

def print_report(report: ConversionReport, directory: Path) -> None:
    print(f"Projects found : {report.count}")
    print(f"Converted      : {report.converted}")
    print(f"Skipped        : {report.skipped}")
    print(f"Failed         : {report.failed}")
    if report.failures:
        print()
        print("Failed projects:")

        for failure in report.failures:
            relative = failure.source.relative_to(directory)

            print(f"  {relative}")
            print(f"      {failure.reason}")

def run() -> int:
    args = parse_args()

    if not args.directory.is_dir():
        print(
            f"Error: '{args.directory}' is not a directory.",
            file=sys.stderr,
        )
        return 1

    report = convert_directory(
        args.directory,
        dry_run=args.dry_run,
    )

    print_report(report, args.directory)

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

if __name__ == "__main__":
    raise SystemExit(main())
