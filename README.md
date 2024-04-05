# nested-config README

**nested-config** is a simple extension to `BaseModel` from
[**pydantic**](https://github.com/samuelcolvin/pydantic/) which adds TOML parsing and JSON serialization of
PurePosixPath objects.

## Purpose

1. Provide short classmethod for reading pydantic models from TOML strings or files.
2. Include validation and JSON serialization for PurePosixPath, used for remote destinations (e.g. rsync or
   ssh).

## Usage

```python
from pathlib import PurePosixPath

from nested_config import BaseModel  # subclasses BaseModel from pydantic


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

## Pydantic 1.0/2.0 Compatibility

nested-config is runtime compatible with Pydantic 1.8+ and Pydantic 2.0.

The follow table gives info on how to configure the [mypy](https://www.mypy-lang.org/) and
[Pyright](https://microsoft.github.io/pyright) type checkers to properly work, depending
on the version of Pydantic you are using.

| Pydantic Version | [mypy config][1]            | mypy cli                    | [Pyright config][2]                         |
|------------------|-----------------------------|-----------------------------|---------------------------------------------|
| 2.0+             | `always_false = PYDANTIC_1` | `--always-false PYDANTIC_1` | `defineConstant = { "PYDANTIC_1" = false }` |
| 1.8-1.10         | `always_true = PYDANTIC_1`  | `--always-true PYDANTIC_1`  | `defineConstant = { "PYDANTIC_1" = true }`  |

[1]: https://mypy.readthedocs.io/en/latest/config_file.html
[2]: https://microsoft.github.io/pyright/#/configuration

## Changelog

### [Unreleased]

- Add validators for `PurePath` and `PureWindowsPath`
- Simplify JSON encoder specification to work for all `PurePaths`
- Add ability to interpret a string value in a field that should be a sub-model as a path
  to another TOML file to enable nested configurations.

### [1.1.3] - 2021-07-30

- Add README
- Simplify PurePosixPath validator
- Export `TomlParsingError` from rtoml for downstream exception handling (without needing to explicitly
  import rtoml).

[Unreleased]: https://gitlab.com/osu-nrsg/nested-config/-/compare/v1.1.3...master
[1.1.3]: https://gitlab.com/osu-nrsg/nested-config/-/tags/v1.1.3
