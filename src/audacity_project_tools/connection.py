import os
from pathlib import Path

from .pipe import AudacityPipe


def connect() -> AudacityPipe:
    uid = os.getuid()

    to_pipe = Path(
        f"/tmp/audacity_script_pipe.to.{uid}"
    )

    from_pipe = Path(
        f"/tmp/audacity_script_pipe.from.{uid}"
    )

    pipe = AudacityPipe(
        to_pipe,
        from_pipe,
    )

    pipe.connect()

    return pipe
