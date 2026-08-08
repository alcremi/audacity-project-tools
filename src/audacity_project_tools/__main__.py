import sys
import logging
from pathlib     import Path

from .api        import convert_directory, format_report
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
        output_dir=args.output_dir,
        dry_run=args.dry_run,
    )

    text = format_report(report, args.directory)

    print(text)

    report_file = args.directory / "conversion-report.txt"
    report_file.write_text(text, encoding="utf-8",)

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
