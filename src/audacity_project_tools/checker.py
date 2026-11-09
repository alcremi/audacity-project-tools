"""Static integrity checks for Audacity projects (no Audacity process needed)."""

from __future__ import annotations

import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path

from .models import CheckResult

# "AUDY": the SQLite application_id Audacity stamps on .aup3 files.
AUP3_APPLICATION_ID = 0x41554459

AUP3_REQUIRED_TABLES = {"project", "sampleblocks"}

MAX_INTEGRITY_MESSAGES = 10

# Legacy block file elements and the attributes naming files in the _data directory.
DATA_FILE_ATTRIBUTES = {
    "simpleblockfile": ("filename",),
    "legacyblockfile": ("name",),
    "pcmaliasblockfile": ("summaryfile",),
    "odpcmaliasblockfile": ("summaryfile",),
    "oddecodeblockfile": ("summaryfile",),
}

# Block file elements referencing an external audio file by absolute path.
ALIAS_FILE_ELEMENTS = {
    "pcmaliasblockfile",
    "odpcmaliasblockfile",
    "oddecodeblockfile",
}


def check_project(path: Path) -> CheckResult:
    """Check an Audacity project file for corruption."""

    if not path.is_file():
        return CheckResult(path=path, problems=[f"File not found: {path}"])

    match path.suffix.lower():
        case ".aup3":
            problems = _check_aup3(path)
        case ".aup":
            problems = _check_aup(path)
        case _:
            problems = [f"Not an Audacity project (.aup or .aup3): {path.name}"]

    return CheckResult(path=path, problems=problems)


def _check_aup3(path: Path) -> list[str]:
    try:
        connection = sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)
    except sqlite3.Error as exc:
        return [f"Cannot open SQLite database: {exc}"]

    try:
        problems: list[str] = []

        (application_id,) = connection.execute("PRAGMA application_id").fetchone()
        if application_id != AUP3_APPLICATION_ID:
            problems.append("Not an Audacity database (wrong application_id).")

        tables = {
            name
            for (name,) in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        missing = AUP3_REQUIRED_TABLES - tables
        if missing:
            problems.append(f"Missing tables: {', '.join(sorted(missing))}")

        for (message,) in connection.execute(
            f"PRAGMA integrity_check({MAX_INTEGRITY_MESSAGES})"
        ):
            if message != "ok":
                problems.append(f"SQLite integrity: {message}")

        if "project" in tables:
            (project_rows,) = connection.execute(
                "SELECT COUNT(*) FROM project"
            ).fetchone()
            if project_rows == 0:
                problems.append("Project table is empty.")

        return problems

    except sqlite3.DatabaseError as exc:
        return [f"Corrupted database: {exc}"]

    finally:
        connection.close()


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _check_aup(path: Path) -> list[str]:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        return [f"Invalid XML: {exc}"]

    if _local_name(root.tag) != "project":
        return ["Root element is not <project>."]

    data_dir = path.with_name(root.get("projname") or f"{path.stem}_data")

    referenced: list[str] = []
    aliases: list[str] = []

    for element in root.iter():
        name = _local_name(element.tag)

        for attribute in DATA_FILE_ATTRIBUTES.get(name, ()):
            value = element.get(attribute)
            if value:
                referenced.append(value)

        if name in ALIAS_FILE_ELEMENTS:
            alias = element.get("aliasfile")
            if alias:
                aliases.append(alias)

    problems: list[str] = []

    if referenced:
        if not data_dir.is_dir():
            return [f"Missing data directory: {data_dir.name}"]

        available = {file.name for file in data_dir.rglob("*") if file.is_file()}
        missing = [name for name in referenced if name not in available]

        if missing:
            problems.append(
                f"{len(missing)} of {len(referenced)} block files missing "
                f"in {data_dir.name} (first: {missing[0]})"
            )

    missing_aliases = sorted({alias for alias in aliases if not Path(alias).is_file()})
    for alias in missing_aliases:
        problems.append(f"Missing aliased audio file: {alias}")

    return problems


def format_check_result(result: CheckResult) -> str:
    """Return a human-readable check result."""

    if result.ok:
        return f"OK        {result.path}\n"

    lines = [f"CORRUPTED {result.path}"]
    lines.extend(f"    {problem}" for problem in result.problems)

    return "\n".join(lines) + "\n"
