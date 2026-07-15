from pathlib import Path

from audacity_project_tools import AudacityPipe


def test_pipe_creation() -> None:
    pipe = AudacityPipe(
        Path("/tmp/to"),
        Path("/tmp/from"),
    )

    assert pipe is not None
    assert pipe._reader is None
    assert pipe._writer is None
