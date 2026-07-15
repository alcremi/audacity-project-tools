from pathlib import Path

from audacity_project_tools import AudacityPipe
from audacity_project_tools import AudacityClient
from audacity_project_tools import FakePipe

def test_client() -> None:
    pipe = FakePipe()
    client = AudacityClient(pipe)
    client.help()
    assert pipe.command == "Help:"
