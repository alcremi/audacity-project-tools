from collections.abc import Iterator
from pathlib import Path


class ProjectScanner:
    """Discover Audacity projects in a directory tree."""

    def scan(
        self,
        root: Path,
        pattern: str = "*.aup",
    ) -> Iterator[Path]:
        """Yield Audacity projects matching *pattern*."""

        for path in sorted(root.rglob(pattern)):
            yield path
