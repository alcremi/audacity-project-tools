from pathlib import Path

import time
import logging

from .client import AudacityClient

logger = logging.getLogger(__name__)


class ProjectConverter:
    """Convert legacy Audacity projects."""

    def __init__(self, client: AudacityClient) -> None:
        self._client = client

    def convert(
            self,
            source: Path,
            destination: Path,
    ) -> None:
        logger.info(
            "Converting %s -> %s",
            source,
            destination,
        )
        project = self._client.load_project(source)

        self._client.save_project(destination)
