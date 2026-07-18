from pathlib import Path

from audacity_project_tools import FakePipe3
from audacity_project_tools import AudacityClient
from audacity_project_tools import ProjectConverter


def test_converter_creation() -> None:
    pipe = FakePipe3()

    client = AudacityClient(pipe)

    converter = ProjectConverter(client)

    assert converter is not None


def test_converter_convert() -> None:
    pipe = FakePipe3()

    client = AudacityClient(pipe)

    converter = ProjectConverter(client)
