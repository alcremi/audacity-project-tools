from pathlib import Path

import time
import logging

from .client     import AudacityClient
from .exceptions import ConversionError

logger = logging.getLogger(__name__)


class ProjectConverter:
    """Convert legacy Audacity projects."""

    def __init__(
            self,
            client,
            save_timeout: float = 5.0,
    ):
        self._client = client
        self._save_timeout = save_timeout

    def _wait_for_saved_project(
            self,
            destination: Path,
    ) -> None:
        timeout = 5.0
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            if destination.exists():
                return

            time.sleep(0.1)

        raise ConversionError(
            f"{destination} was not created."
        )

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
        self._client.load_project(source)

        self._client.save_project(destination)

        deadline = time.monotonic() + 5

        while time.monotonic() < deadline:
            if destination.exists():
                return

            time.sleep(0.1)

        raise ConversionError(
            f"Destination file '{destination}' was not created."
        )
