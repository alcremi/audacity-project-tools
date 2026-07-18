from collections.abc import Iterator

from pathlib import Path


class ProjectScanner:
    """Discover Audacity projects in a directory tree."""

    def scan(self, root: Path) -> Iterator[Path]:
        """Yield all legacy Audacity project files under *root*."""

        for path in sorted(root.rglob("*.aup")):
            yield path
