# pydantic-plus README

**pydantic-plus** is a simple extension to `BaseModel` from
[**pydantic**](https://github.com/samuelcolvin/pydantic/) which adds TOML parsing and JSON serialization of
PurePosixPath objects.

## Purpose

1. Provide short classmethod for reading pydantic models from TOML strings or files.
2. Include validation and JSON serialization for PurePosixPath, used for remote destinations (e.g. rsync or
   ssh).

## Usage

```python
from pathlib import PurePosixPath

from pydantic_plus import BaseModel  # subclasses BaseModel from pydantic


class MyModel(BaseModel):
    remote_server: str
    remote_path: PurePosixPath


toml_str = '''\
remote_server = "rsync.example.com"
remote_path = "shared/documents/report.xls"
'''

my_model = MyModel.from_tomls(toml_str)  # can also use .from_toml to read from file.

my_model  # MyModel(remote_server='rsync.example.com', remote_path=PurePosixPath('shared/documents/report.xls'))
my_model.json()  # '{"remote_server": "rsync.example.com", "remote_path": "shared/documents/report.xls"}'

```
