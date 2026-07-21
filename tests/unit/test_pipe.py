from pathlib import Path

from audacity_project_tools.pipe import AudacityPipe, PIPE_TO, PIPE_FROM


def test_pipe_creation() -> None:
    pipe = AudacityPipe(
        Path("/tmp/to"),
        Path("/tmp/from"),
    )

    assert pipe is not None
    assert pipe._reader is None
    assert pipe._writer is None


def test_default_pipe() -> None:
    pipe = AudacityPipe.default()

    assert pipe._to_pipe == PIPE_TO
    assert pipe._from_pipe == PIPE_FROM
