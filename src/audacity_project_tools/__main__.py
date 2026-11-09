import sys
import logging
from pathlib     import Path

from .api        import convert_directory, format_report
from .checker    import check_project, format_check_result
from .cli        import parse_args, validate_args
from .exceptions import PipeConnectionError


def run() -> int:
    args = parse_args()

    logging.basicConfig(
        filename="audacity-project-tools.log",
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    try:
        validate_args(args)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.check is not None:
        result = check_project(args.check)
        print(format_check_result(result), end="")
        return 0 if result.ok else 1

    if not args.directory.is_dir():
        print(
            f"Error: '{args.directory}' is not a directory.",
            file=sys.stderr,
        )
        return 1

    report = convert_directory(
        args.directory,
        mode=args.mode,
        output_dir=args.output_dir,
        dry_run=args.dry_run,
    )

    text = format_report(report, args.directory)

    print(text, end="")

    report_file = args.directory / "conversion-report.txt"
    report_file.write_text(text, encoding="utf-8",)

    return 0


def main() -> int:
    try:
        return run()
    except PipeConnectionError:
        print("Error: Audacity is not running.", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
