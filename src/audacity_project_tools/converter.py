from pathlib import Path

from .client import AudacityClient


class ProjectConverter:
    """Convert legacy Audacity projects."""

    def __init__(self, client: AudacityClient) -> None:
        self._client = client

    def convert(
            self,
            source: Path,
            destination: Path,
    ) -> None:
        project = self._client.load_project(source)

        self._client.save_project(destination)
