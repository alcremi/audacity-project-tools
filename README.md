# audacity-project-tools

Convert legacy Audacity projects automatically.

## Features

- Connect to Audacity through `mod-script-pipe`
- Load legacy `.aup` projects
- Save projects as modern `.aup3`
- Scan directories recursively for Audacity projects
- Convert multiple projects automatically

## Requirements

- Python 3.13 or newer
- Audacity with the `mod-script-pipe` module enabled

## Installation

```bash
git clone https://github.com/alcremi/audacity-project-tools.git
cd audacity-project-tools

python -m venv .venv
source .venv/bin/activate

pip install -e .
```

## Example

```python
from pathlib import Path

from audacity_project_tools.connection import connect
from audacity_project_tools import (
    AudacityClient,
    ProjectConverter,
)

pipe = connect()
client = AudacityClient(pipe)

converter = ProjectConverter(client)

converter.convert(
    Path("old.aup"),
    Path("new.aup3"),
)

client.exit()
```

## Command line

```bash
python -m audacity_project_tools
```

(Command-line options will be extended in future releases.)

## Project status

This project is currently under active development.

The public API is still evolving.

## License

MIT License
