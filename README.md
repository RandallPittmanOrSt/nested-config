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
   respective Pydantic models using `pyd_obj_from_config()`. The `default_suffix` kwarg
   allows for specifying the file suffix (extension) to assume if the config file has no
   suffix or its suffix is not in the `nested_config.config_dict_loaders` dict.

   Example including mixed configuration file types and `default_suffix` (Note that PyYAML
   is an extra dependency required for parsing yaml files):

   **house.yaml**

   ```yaml
   name: my house
   dimensions: dimensions
   ```

   **dimensions** (TOML type)

   ```toml
   length = 10
   width = 20
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


   house = pyd_obj_from_config("house.yaml", House)
   house  # House(name='my house', dimensions=Dimensions(length=10, width=20))
   ```

2. Alternatively, you can use `nested_config.BaseModel` which subclasses
   `pydantic.BaseModel` and adds a `from_config` classmethod to simplify the code:

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


   house = House.from_config("house.toml", House)
   house  # House(name='my house', dimensions=Dimensions(length=12.6, width=25.3))
   ```

   In this case, if you need to specify a default loader, just use
   `nested_config.set_default_loader(suffix)` before using `BaseModel.from_config()`.

A bonus feature of **nested-config** is that it provides for validation and JSON encoding
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

See [tests](tests) for more detailed use-cases.

### Included loaders

**nested-config** automatically loads the following files based on extension:

| Format | Extensions(s) | Library                                    |
| ------ | ------------- | ------------------------------------------ |
| JSON   | .json         | `json` (stdlib)                            |
| TOML   | .toml         | `tomllib` (Python 3.11+ stdlib) or `tomli` |
| YAML   | .yaml, .yml   | `pyyaml` (extra dependency[^yaml-extra])   |

[^yaml-extra]: Install `pyyaml` separately with `pip` or install **nested-config** with
               `pip install nested_config[yaml]`.

### Adding loaders

To add a loader for another file extension, simply update the `config_dict_loaders` dict:

```python
import nested_config
from nested_config import ConfigDict  # alias for dict[str, Any]

def dummy_loader(config_path: Path) -> ConfigDict:
    return {"a": 1, "b": 2}

nested_config.config_dict_loaders[".dmy"] = dummy_loader

# or add another extension for an existing loader
nested_config.config_dict_loaders[".jsn"] = nested_config.config_dict_loaders[".json"]
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
