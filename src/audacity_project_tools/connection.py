from pathlib import Path

from .process import AudacityProcess
from .pipe    import AudacityPipe
from .client  import AudacityClient


def connect() -> AudacityClient:
    process = AudacityProcess()

    process.start()
    process.wait_until_ready()

    pipe = AudacityPipe.default()
    pipe.connect()

    return AudacityClient(pipe)
