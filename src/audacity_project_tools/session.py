from __future__ import annotations

from .client  import AudacityClient
from .pipe    import AudacityPipe
from .process import AudacityProcess


class AudacitySession:
    """Manage a complete Audacity session."""

    def __init__(
        self,
        process: AudacityProcess | None = None,
        pipe: AudacityPipe | None = None,
    ) -> None:
        self._process = process if process is not None else AudacityProcess()
        self._pipe = pipe if pipe is not None else AudacityPipe.default()
        self._client: AudacityClient | None = None

    def start(self) -> AudacityClient:
        if self._client is not None:
            return self._client

        self._process.start()
        self._process.wait_until_ready()

        self._pipe.connect()

        self._client = AudacityClient(self._pipe)

        return self._client

    def close(self) -> None:
        if self._client is not None:
            self._client.exit_audacity()

        self._process.wait_for_exit()
