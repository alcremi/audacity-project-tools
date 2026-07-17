from pathlib import Path

from .pipe import AudacityPipe
from .exceptions import AudacityCommandError
from .models import Track, Project
from .parsers import parse_tracks

class AudacityClient:
    """High-level interface to Audacity scripting commands."""

    def __init__(self, pipe: AudacityPipe) -> None:
        self._pipe = pipe

    def _execute(self, command: str) -> str:
        response = self._pipe.send(command)

        if "BatchCommand finished: Failed!" in response:
            raise AudacityCommandError(response)

        return response

    def help(self) -> str:
        """Return the help description from Audacity."""

        return self._execute("Help:")

    def get_tracks(self) -> list[Track]:
        response = self._execute("GetInfo: Type=Tracks")
        return parse_tracks(response)


    def open_project(self, project_path: Path) -> None:
        command = f'OpenProject2: Filename="{project_path}"'
        self._execute(command)

    def save_project(self, project_path: Path) -> None:
        command = f'SaveProject2: Filename="{project_path}"'
        self._execute(command)

    def exit_project(self) -> None:
        command = f'Exit:"'
        self._execute(command)

    def load_project(self, path: Path) -> Project:
        self.open_project(path)

        tracks = self.get_tracks()

        return Project(
            path=path,
            tracks=tracks,
        )
