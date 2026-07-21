from unittest.mock import patch

from pathlib import Path

from audacity_project_tools.process import AudacityProcess


def test_start() -> None:
    with patch("subprocess.Popen") as popen:
        process = AudacityProcess()

        process.start()

        popen.assert_called_once_with(
            ["audacity"],
            text=True,
        )
