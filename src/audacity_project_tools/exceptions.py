class AudacityError(Exception):
    """Base exception for Audacity project tools."""


class PipeConnectionError(AudacityError):
    """Raised when the connection to Audacity pipes fails."""


class CommandError(AudacityError):
    """Raised when Audacity rejects a command."""

class AudacityCommandError(Exception):
    """Raised when Audacity reports a command failure."""
