from pathlib import Path
import time

from .exceptions import AudacityCommandError
from .models     import Track, Project
from .parsers    import parse_tracks
from .pipe       import AudacityPipe

class AudacityClient:
    """High-level interface to Audacity scripting commands."""

    def __init__(self, pipe: AudacityPipe) -> None:
        self._pipe = pipe

    def _clean_response(self, response: str) -> str:
        marker = "BatchCommand finished:"

        if marker in response:
            return response.split(marker, 1)[0]

        return response

    def _execute(self, command: str) -> str:
        """Execute an Audacity command and return its response."""

        response = self._pipe.send(command)

        if "BatchCommand finished: Failed!" in response:
            raise AudacityCommandError(response)

        return self._clean_response(response)

    def help(self) -> str:
        """Return the help description from Audacity."""

        return self._execute("Help:")

    def get_tracks(self) -> list[Track]:
        response = self._execute("GetInfo: Type=Tracks")

        return parse_tracks(response)

    def _wait_until_project_loaded(self) -> None:
        """Wait until the project is fully loaded."""

        timeout = 10.0
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            try:
                self.get_tracks()
            except AudacityCommandError:
                time.sleep(0.1)
            else:
                return

        raise AudacityCommandError(
            "Timed out while waiting for the project to load."
        )

    def open_project(self, project_path: Path) -> None:
        command = f'OpenProject2: Filename="{project_path}"'
        self._pipe.send(command)
        self._wait_until_project_loaded()

    def save_project(self, project_path: Path) -> None:
        command = f'SaveProject2: Filename="{project_path}"'
        self._execute(command)

    def exit_audacity(self) -> None:
        """Close the project (which must have been saved before) and close the Audacity instance."""

        self._execute("Exit:")

    def load_project(self, path: Path) -> Project:
        self.open_project(path)

        tracks = self.get_tracks()

        return Project(
            path=path,
            tracks=tracks,
        )
