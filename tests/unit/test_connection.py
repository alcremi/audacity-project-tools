from pathlib import Path

from audacity_project_tools import AudacityPipe
from audacity_project_tools.connection import connect

def test_connection_default() -> AudacityPipe:
    pipe = connect()

    assert pipe is not None
