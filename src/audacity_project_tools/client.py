
from .pipe import AudacityPipe
from .exceptions import AudacityCommandError


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

    def get_tracks(self) -> str:
        return self._execute("GetInfo: Type=Tracks")

    # open_project(...)

    # save_project(...)


class FakePipe:
    def __init__(self) -> None:
        self.command = ""

    def send(self, command: str) -> str:
        self.command = command
        return "BatchCommand finished: OK"
