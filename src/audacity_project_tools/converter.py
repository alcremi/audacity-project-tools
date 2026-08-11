from pathlib import Path

import time
import logging
import shutil

from .client     import AudacityClient
from .exceptions import ConversionError
from .models     import ConversionMode

logger = logging.getLogger(__name__)


class ProjectConverter:
    """Convert legacy Audacity projects."""

    def __init__(
            self,
            client,
            save_timeout: float = 5.0,
            load_timeout: float = 10.0,
    ):
        self._client = client
        self._save_timeout = save_timeout
        self._load_timeout = load_timeout

    def _wait_for_saved_project(
            self,
            destination: Path,
    ) -> None:
        timeout = self._save_timeout
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            if destination.exists():
                return

            time.sleep(0.1)

        raise ConversionError(
            f"{destination} was not created."
        )

    def _convert_aup3_to_aup3(
        self,
        source: Path,
        destination: Path,
    ) -> None:
        temporary = source.with_name(
            f".{source.stem}.conversion.aup3"
        )

        try:
            shutil.copy2(source, temporary)

            self._client.load_project(temporary, timeout=self._load_timeout)
            self._client.save_project(destination)

            self._wait_for_saved_project(destination)

        finally:
            for suffix in ("", "-shm", "-wal"):
                temporary_file = Path(f"{temporary}{suffix}")
                temporary_file.unlink(missing_ok=True)

    def convert(
        self,
        source: Path,
        destination: Path,
        mode: ConversionMode,
    ) -> None:
        logger.info(
            "Converting %s -> %s",
            source,
            destination,
        )

        if mode == ConversionMode.AUP3_TO_AUP3:
            self._convert_aup3_to_aup3(
                source,
                destination,
            )
            return

        self._client.load_project(source)
        self._client.save_project(destination)

        self._wait_for_saved_project(destination)
