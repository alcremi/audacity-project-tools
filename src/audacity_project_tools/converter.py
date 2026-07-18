from pathlib import Path

from .client import AudacityClient


class ProjectConverter:
    """Convert legacy Audacity projects."""

    def __init__(self, client: AudacityClient) -> None:
        self._client = client
