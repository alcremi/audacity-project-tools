from pathlib import Path

from audacity_project_tools import ProjectScanner


def test_scan_empty_directory(tmp_path: Path) -> None:
    scanner = ProjectScanner()

    assert list(scanner.scan(tmp_path)) == []

def test_scan_one_project(tmp_path: Path) -> None:
    (tmp_path / "song.aup").touch()

    scanner = ProjectScanner()

    assert list(scanner.scan(tmp_path)) == [
        tmp_path / "song.aup",
    ]

def test_scan_recursive(tmp_path: Path) -> None:
    project = tmp_path / "albums" / "live"

    project.mkdir(parents=True)

    (project / "concert.aup").touch()

    scanner = ProjectScanner()

    assert list(scanner.scan(tmp_path)) == [
        project / "concert.aup",
    ]
