from pathlib     import Path

class AudacityError(Exception):
    """Base exception for Audacity project tools."""


class PipeConnectionError(AudacityError):
    """Raised when the connection to Audacity pipes fails."""

class DirectoryNotFoundError(AudacityError):
    """Raised when the root directory does not exist."""
    def __init__(self, directory: Path) -> None:
        self.directory = directory
        super().__init__(str(directory))


class CommandError(AudacityError):
    """Raised when Audacity rejects a command."""

class AudacityCommandError(Exception):
    """Raised when Audacity reports a command failure."""

class AudacityProcessError(Exception):
    """Audacity process management error."""
