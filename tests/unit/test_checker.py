import sqlite3
from pathlib import Path

from audacity_project_tools.checker import (
    AUP3_APPLICATION_ID,
    check_project,
    format_check_result,
)

AUP_TEMPLATE = """<?xml version="1.0" standalone="no" ?>
<project xmlns="http://audacity.sourceforge.net/xml/" projname="song_data">
  <wavetrack name="t">
    <waveclip offset="0">
      <sequence>
        <waveblock start="0">{block}</waveblock>
      </sequence>
    </waveclip>
  </wavetrack>
</project>
"""


def make_aup(tmp_path: Path, block: str) -> Path:
    project = tmp_path / "song.aup"
    project.write_text(AUP_TEMPLATE.format(block=block), encoding="utf-8")
    return project


def make_aup3(
    path: Path,
    application_id: int = AUP3_APPLICATION_ID,
    with_project_row: bool = True,
) -> Path:
    connection = sqlite3.connect(path)
    connection.execute(f"PRAGMA application_id = {application_id}")
    connection.execute("CREATE TABLE project (id INTEGER PRIMARY KEY, doc BLOB)")
    connection.execute("CREATE TABLE sampleblocks (blockid INTEGER PRIMARY KEY, samples BLOB)")
    if with_project_row:
        connection.execute("INSERT INTO project (doc) VALUES (x'00')")
    connection.commit()
    connection.close()
    return path


def test_valid_aup(tmp_path: Path) -> None:
    project = make_aup(tmp_path, '<simpleblockfile filename="e0001.au"/>')
    blocks = tmp_path / "song_data" / "e00" / "d00"
    blocks.mkdir(parents=True)
    (blocks / "e0001.au").write_bytes(b"")

    assert check_project(project).ok


def test_aup_missing_block_file(tmp_path: Path) -> None:
    project = make_aup(tmp_path, '<simpleblockfile filename="e0001.au"/>')
    (tmp_path / "song_data").mkdir()

    result = check_project(project)

    assert not result.ok
    assert "1 of 1 block files missing" in result.problems[0]


def test_aup_missing_data_directory(tmp_path: Path) -> None:
    project = make_aup(tmp_path, '<simpleblockfile filename="e0001.au"/>')

    result = check_project(project)

    assert result.problems == ["Missing data directory: song_data"]


def test_aup_missing_aliased_file(tmp_path: Path) -> None:
    (tmp_path / "song_data").mkdir()
    (tmp_path / "song_data" / "s.auf").write_bytes(b"")
    project = make_aup(
        tmp_path,
        f'<pcmaliasblockfile summaryfile="s.auf" aliasfile="{tmp_path}/gone.wav"/>',
    )

    result = check_project(project)

    assert result.problems == [f"Missing aliased audio file: {tmp_path}/gone.wav"]


def test_aup_invalid_xml(tmp_path: Path) -> None:
    project = tmp_path / "song.aup"
    project.write_text("<project><wavetrack>", encoding="utf-8")

    result = check_project(project)

    assert not result.ok
    assert result.problems[0].startswith("Invalid XML")


def test_valid_aup3(tmp_path: Path) -> None:
    assert check_project(make_aup3(tmp_path / "song.aup3")).ok


def test_aup3_wrong_application_id(tmp_path: Path) -> None:
    result = check_project(make_aup3(tmp_path / "song.aup3", application_id=0))

    assert "wrong application_id" in result.problems[0]


def test_aup3_empty_project_table(tmp_path: Path) -> None:
    result = check_project(make_aup3(tmp_path / "song.aup3", with_project_row=False))

    assert result.problems == ["Project table is empty."]


def test_aup3_not_a_database(tmp_path: Path) -> None:
    project = tmp_path / "song.aup3"
    project.write_bytes(b"garbage" * 100)

    result = check_project(project)

    assert not result.ok
    assert "not a database" in result.problems[0]


def test_missing_file(tmp_path: Path) -> None:
    assert not check_project(tmp_path / "nope.aup3").ok


def test_unknown_extension(tmp_path: Path) -> None:
    other = tmp_path / "notes.txt"
    other.write_text("hello")

    assert not check_project(other).ok


def test_format_check_result(tmp_path: Path) -> None:
    project = tmp_path / "song.aup"
    project.write_text("<broken", encoding="utf-8")

    text = format_check_result(check_project(project))

    assert text.startswith(f"CORRUPTED {project}\n    Invalid XML")
