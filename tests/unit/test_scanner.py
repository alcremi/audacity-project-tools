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

def test_scan_finds_aup_files(tmp_path: Path) -> None:
    first = tmp_path / "first.aup"
    second = tmp_path / "second.aup"
    other = tmp_path / "other.txt"

    first.touch()
    second.touch()
    other.touch()

    scanner = ProjectScanner()

    result = list(scanner.scan(tmp_path))

    assert result == [
        first,
        second,
    ]

def test_scan_finds_aup3_files(tmp_path: Path) -> None:
    first = tmp_path / "first.aup3"
    second = tmp_path / "second.aup3"
    other = tmp_path / "other.aup"

    first.touch()
    second.touch()
    other.touch()

    scanner = ProjectScanner()

    result = list(scanner.scan(tmp_path, "*.aup3"))

    assert result == [
        first,
        second,
    ]

def test_scan_finds_projects_in_subdirectories(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "Audio"
    directory.mkdir()

    project = directory / "project.aup3"
    project.touch()

    scanner = ProjectScanner()

    result = list(scanner.scan(tmp_path, "*.aup3"))

    assert result == [project]


def test_scan_ignores_directories_matching_pattern(
    tmp_path: Path,
) -> None:
    project_directory = tmp_path / "fake.aup"
    project_directory.mkdir()

    project = tmp_path / "real.aup"
    project.touch()

    scanner = ProjectScanner()

    assert list(scanner.scan(tmp_path)) == [
        project,
    ]
