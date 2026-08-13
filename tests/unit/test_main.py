from pathlib import Path

from audacity_project_tools        import __main__ as main_module
from audacity_project_tools.models import ConversionMode, ConversionReport


def test_run_returns_error_for_missing_directory(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    missing = tmp_path / "does-not-exist"

    class FakeArgs:
        directory = missing
        mode = None
        output_dir = None
        dry_run = False

    monkeypatch.setattr(
        main_module,
        "parse_args",
        lambda: FakeArgs(),
    )

    monkeypatch.setattr(
        main_module,
        "validate_args",
        lambda args: None,
    )

    result = main_module.run()

    captured = capsys.readouterr()

    assert result == 1
    assert (
        f"Error: '{missing}' is not a directory."
        in captured.err
    )


def test_run_converts_directory_and_writes_report(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    class FakeArgs:
        directory = tmp_path
        mode = ConversionMode.AUP_TO_AUP3
        output_dir = tmp_path / "converted"
        dry_run = False

    report = ConversionReport(
        count=2,
        converted=2,
        skipped=0,
        failed=0,
    )

    calls: dict[str, object] = {}

    def fake_convert_directory(
        directory: Path,
        *,
        mode: ConversionMode,
        output_dir: Path | None,
        dry_run: bool,
    ) -> ConversionReport:
        calls["directory"] = directory
        calls["mode"] = mode
        calls["output_dir"] = output_dir
        calls["dry_run"] = dry_run
        return report

    def fake_format_report(
        received_report: ConversionReport,
        directory: Path,
    ) -> str:
        calls["report"] = received_report
        calls["report_directory"] = directory
        return "Conversion report\n"

    monkeypatch.setattr(
        main_module,
        "parse_args",
        lambda: FakeArgs(),
    )
    monkeypatch.setattr(
        main_module,
        "validate_args",
        lambda args: None,
    )
    monkeypatch.setattr(
        main_module,
        "convert_directory",
        fake_convert_directory,
    )
    monkeypatch.setattr(
        main_module,
        "format_report",
        fake_format_report,
    )

    result = main_module.run()

    captured = capsys.readouterr()

    assert result == 0

    assert calls == {
        "directory": tmp_path,
        "mode": ConversionMode.AUP_TO_AUP3,
        "output_dir": tmp_path / "converted",
        "dry_run": False,
        "report": report,
        "report_directory": tmp_path,
    }

    assert captured.out == "Conversion report\n"

    report_file = tmp_path / "conversion-report.txt"

    assert report_file.exists()
    assert report_file.read_text(encoding="utf-8") == (
        "Conversion report\n"
    )


def test_main_returns_error_if_audacity_is_not_running(
    monkeypatch,
    capsys,
) -> None:
    def fake_run() -> int:
        raise main_module.PipeConnectionError()

    monkeypatch.setattr(
        main_module,
        "run",
        fake_run,
    )

    result = main_module.main()

    captured = capsys.readouterr()

    assert result == 1
    assert captured.out == ""
    assert captured.err == (
        "Error: Audacity is not running.\n"
    )
