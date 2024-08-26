# nested-config <!-- omit in toc -->

[![PyPI package](https://img.shields.io/pypi/v/nested-config.svg)](http://python.org/pypi/nested-config)&nbsp;&nbsp;
[GitLab repository](https://gitlab.com/osu-nrsg/nested-config)&nbsp;&nbsp;
[GitHub mirror](https://github.com/RandallPittmanOrSt/nested-config)

<span style="font-size: larger">If you've ever wanted to have the option of replacing part
 of a configuration file with a path to another configuration file that contains those
sub-parameters, then _nested-config_ might be for you.</span>

_nested-config_ allows you to parse configuration files that contain references to other
configuration files using a series of [models](#model). If a model includes a [nested
model](#nested-model) as one of its attributes and _nested-config_ finds a string value
for that parameter in the configuration file instead of an associative
array[^assoc-array], then it assumes that this string is a path to another configuration
file that should be parsed and whose contents should replace the string in the main
configuration file. If the string appears to be a relative path, it is assumed to be
relative to the path of its parent configuration file.

## Contents

- [Contents](#contents)
- [Basic Usage](#basic-usage)
- [Nomenclature](#nomenclature)
  - [loader](#loader)
  - [model](#model)
  - [nested model](#nested-model)
  - [config dict](#config-dict)
- [API](#api)
  - [`nested_config.expand_config(config_path, model, *, default_suffix = None)`](#nested_configexpand_configconfig_path-model--default_suffix--none)
  - [`nested_config.config_dict_loaders`](#nested_configconfig_dict_loaders)
    - [Included loaders](#included-loaders)
    - [Adding loaders](#adding-loaders)
  - [_Deprecated features in v2.1.0, to be removed in v3.0.0_](#deprecated-features-in-v210-to-be-removed-in-v300)
- [Pydantic 1.0/2.0 Compatibility](#pydantic-1020-compatibility)
- [Footnotes](#footnotes)

## Basic Usage

Given the following configuration files `/tmp/house.toml` and `/tmp/tmp2/dimensions.toml`:

<figure>
<figcaption>Figure 1: /tmp/house.toml</figcaption>

```toml
name = "my house"
dimensions = "tmp2/dimensions.toml"
```

</figure>

<figure>
<figcaption>Figure 2: /tmp/tmp2/dimensions.toml</figcaption>

```toml
length = 10
width = 20
```

</figure>

You can expand these into a single dict with the following:

<figure>
<figcaption>Figure 3: Expand /tmp/house.toml</figcaption>

```python
import nested_config

class Dimensions:
    length: int
    width: int


class House:
    name: str
    dimensions: Dimensions


house_dict = nested_config.expand_config("/tmp/house.toml", House)
print(house_dict)
# {'name': 'my house', 'dimensions': {'length': 10, 'width': 20}}
```

Note that in `/tmp/house.toml`, `dimensions` is not a mapping but is a path to another
toml file at a path relative to `house.toml`.

See [tests](https://gitlab.com/osu-nrsg/nested-config/-/tree/master/tests) for more
detailed use-cases, such as where the root model contains lists or dicts of other models
and when those may be included in the root config file or specified as paths to sub-config
files.

## Nomenclature

### loader

A _loader_ is a function that reads a config file and returns a `dict` containing the
key-value pairs from the file. _nested-config_ includes loaders for JSON, TOML, and (if
PyYAML is installed) YAML. For example, the JSON loader looks like this:

```python
import json

def json_load(path):
    with open(path, "rb") as fobj:
        return json.load(fobj)
```

### model

_nested-config_ uses the term _model_ to refer to a class definition that includes
annotated attributes. For example, this model, `Dimensions`, includes three attributes,
each of float type, `x`, `y`, and `z`:

```python
class Dimensions:
    x: float
    y: float
    z: float
```

A model can be decorated as a [dataclass][dataclasses] or using [`attrs.define`][attrs] or
can subclass [`pydantic.BaseModel`][pydantic] to provide some method for instantiating an
object instance of the model but they aren't necessary to use _nested-config_.

The only criterion for a type to be a model is that is has a `__dict__` attribute that
includes an `__annotations__` member. _Note: This does **not** mean that **instances** of
the model must have a `__dict__` attribute. For example, instances of classes with
`__slots__` and `NamedTuple` instances may not have a `__dict__` attribute._

### nested model

A _nested model_ is a model that is included within another model as one of its class
attributes. For example, the below model `House` includes an `name` of string type, and an
attribute `dimensions` of `Dimensions` type (defined above). Since `Dimensions` is a
_model_ type, this is an example of a _nested model_.

```python
class House:
    name: str
    dimensions: Dimensions
```

### config dict

A _config dict_ is simply a `dict` with string keys such as may be obtained by reading in
configuration text. For example reading in a string of TOML text with `tomllib.loads`
returns a _config dict_.

```python
import tomllib

config = "x = 2\ny = 3"
print(tomllib.loads(config))
# {'x': 2, 'y': 3}
```

## API

### `nested_config.expand_config(config_path, model, *, default_suffix = None)`

This function first loads the config file at `config_path` into a [config
dict](#config-dict) using the appropriate [loader](#loader). It then uses the attribute
annotations of [`model`](#model) and/or any [nested models](#nested-model) within `model`
to see if any of the string values in the configuration file correspond to a nested model.
For each such case, the string is assumed to be a path and is loaded into another config
dict which replaces the string value in the parent config dict. This continues until all
paths are converted and then the fully-expanded config dict is returned.

Note that all non-absolute string paths are assumed to be relative to the path of their
parent config file.

The loader for a given config file is determined by file extension (AKA suffix). If
`default_suffix` is specified, any config file with an unknown suffix or no suffix will be
assumed to be of that type, e.g. `".toml"`. (Otherwise this is an error.) It is possible
for one config file to include a path to a config file of a different format, so long as
each file has the appropriate suffix and there is a loader for that suffix.

### `nested_config.config_dict_loaders`

`config_dict_loaders` is a `dict` that maps file suffixes to [loaders](#loader).

#### Included loaders

_nested-config_ automatically loads the following files based on extension:

| Format | Extensions(s) | Library                                    |
| ------ | ------------- | ------------------------------------------ |
| JSON   | .json         | `json` (stdlib)                            |
| TOML   | .toml         | `tomllib` (Python 3.11+ stdlib) or `tomli` |
| YAML   | .yaml, .yml   | `pyyaml` (extra dependency[^yaml-extra])   |

#### Adding loaders

To add a loader for another file extension, simply update `config_dict_loaders`:

```python
import nested_config
from nested_config import ConfigDict  # alias for dict[str, Any]

def dummy_loader(config_path: Path | str) -> ConfigDict:
    return {"a": 1, "b": 2}

nested_config.config_dict_loaders[".dmy"] = dummy_loader

# or add another extension for an existing loader
nested_config.config_dict_loaders[".jsn"] = nested_config.config_dict_loaders[".json"]

# or use a different library to replace an existing loader
import rtoml

def rtoml_load(path) -> ConfigDict:
    with open(path, "rb") as fobj:
        return rtoml.load(fobj)

nested_config.config_dict_loaders[".toml"] = rtoml_load
```

### _Deprecated features in v2.1.0, to be removed in v3.0.0_

The following functionality is available only if Pydantic is installed:

- `nested_config.validate_config()` expands a configuration file according to a Pydantic
  model and then validates the config dictionary into an instance of the Pydantic model.
- `nested_config.BaseModel` can be used as a replacement for `pydantic.BaseModel` to
  include a `from_config()` classmethod on all models that uses
  `nested_config.validate_config()` to create an instance of the model.
- By importing `nested_config`, `PurePath` validators and JSON encoders are added to
  `pydantic` in Pydantic 1.8-1.10 (they are included in Pydantic 2.0+)

## Pydantic 1.0/2.0 Compatibility

The [pydantic functionality](#deprecated-features-in-v210-to-be-removed-in-v300) in
nested-config is runtime compatible with Pydantic 1.8+ and Pydantic 2.0.

The follow table gives info on how to configure the [mypy](https://www.mypy-lang.org/) and
[Pyright](https://microsoft.github.io/pyright) type checkers to properly work, depending
on the version of Pydantic you are using.

| Pydantic Version | [mypy config][1]            | mypy cli                    | [Pyright config][2]                         |
|------------------|-----------------------------|-----------------------------|---------------------------------------------|
| 2.0+             | `always_false = PYDANTIC_1` | `--always-false PYDANTIC_1` | `defineConstant = { "PYDANTIC_1" = false }` |
| 1.8-1.10         | `always_true = PYDANTIC_1`  | `--always-true PYDANTIC_1`  | `defineConstant = { "PYDANTIC_1" = true }`  |

## Footnotes

[^yaml-extra]: Install `pyyaml` separately with `pip` or install _nested-config_ with
               `pip install nested-config[yaml]`.

[^assoc-array]: Each language uses one or more names for an associative arrays. JSON calls
                it an _object_, YAML calls is a _mapping_, and TOML calls is a _table_.
                Any of course in Python it's a _dictionary_, or `dict`.

[1]: https://mypy.readthedocs.io/en/latest/config_file.html
[2]: https://microsoft.github.io/pyright/#/configuration
[dataclasses]: https://docs.python.org/3/library/dataclasses.html
[attrs]: https://www.attrs.org
[pydantic]: https://pydantic.dev
