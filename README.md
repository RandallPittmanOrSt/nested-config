# nested-config README

**nested-config** provides for parsing configuration files that include paths to other
config files into [Pydantic](https://github.com/samuelcolvin/pydantic/) model instances.
It also supports validating and JSON-encoding `pathlib.PurePath` on Pydantic 1.8+.

## Usage

**nested-config** may be used in your project in two main ways.

1. You may simply call `nested_config.pyd_obj_from_config()` with a config file path and a
   Pydantic model which may or may not include nested Pydantic models. If there are nested
   models and the config file has string values for those fields, those values are
   interpreted as paths to other config files and those are recursively read into their
   respective Pydantic models using `pyd_obj_from_config()`. The `loader` kwarg allows the
   use of any config file loader such as `load_yaml` in the below example, or an
   equivalent function for e.g. TOML or JSON.

   Example:

   **house.yaml**

   ```yaml
   name: my house
   dimensions: dimensions.yaml
   ```

   **dimensions.yaml**

   ```yaml
   length: 10
   width: 20
   ```

   **parse_house.py**

   ```python
   import pydantic
   import yaml

   from nested_config import pyd_obj_from_config

   class Dimensions(pydantic.BaseModel):
       length: int
       width: int


   class House(pydantic.BaseModel):
       name: str
       dimensions: Dimensions


   def load_yaml(yaml_path):
       with open(yaml_path, "rb") as fobj:
           return yaml.load(fobj)

   house = pyd_obj_from_config("house.yaml", House, loader=load_yaml)
   house  # House(name='my house', dimensions=Dimensions(length=10, width=20))
   ```

2. Alternatively, if you're using TOML config files, you can use `nested_config.BaseModel`
   which subclasses `pydantic.BaseModel` and adds a `from_toml` classmethod to simplify
   the code:

   **house.toml**

   ```toml
   name = "my house"
   dimensions = "dimensions.toml"
   ```

   **dimensions.toml**

   ```toml
   length = 12.6
   width = 25.3
   ```

   **parse_house.py**

   ```python
   import nested_config

   class Dimensions(nested_config.BaseModel):
       length: float
       width: float


   class House(nested_config.BaseModel):
       name: str
       dimensions: Dimensions


   house = House.from_toml("house.toml", House)
   house  # House(name='my house', dimensions=Dimensions(length=12.6, width=25.3))
   ```

An bonus feature of **nested-config** is that it provides for validation and JSON encoding
of `pathlib.PurePath` and its subclasses in Pydantic <2.0 (this is built into Pydantic
2.0+). All that is needed is an import of `nested_config`. Example:

```python
from pathlib import PurePosixPath

import nested_config
import pydantic


class RsyncDestination(pydantic.BaseModel):
    remote_server: str
    remote_path: PurePosixPath


dest = RsyncDestination(remote_server="rsync.example.com", remote_path="/data/incoming")

dest  # RsyncDestination(remote_server='rsync.example.com', remote_path=PurePosixPath('/data/incoming'))
dest.json()  # '{"remote_server":"rsync.example.com","remote_path":"/data/incoming"}'

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

- ...much more to add here...
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
