from pathlib import Path

from .pipe import AudacityPipe


def connect() -> AudacityPipe:
    pipe = AudacityPipe.default()
    pipe.connect()

    return pipe
