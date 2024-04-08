"""loaders.py - Manage config file loaders"""

import json
import sys
from pathlib import Path
from typing import Dict

if sys.version_info < (3, 11):
    from tomli import load as toml_load_fobj
else:
    from tomllib import load as toml_load_fobj

try:
    import yaml  # type: ignore

    try:
        from yaml import CLoader as YAMLLoader  # type: ignore
    except ImportError:
        from yaml import Loader as YAMLLoader  # type: ignore
except ImportError:
    yaml = None

from nested_config._types import ConfigDict, ConfigDictLoader, PathLike


class NoLoaderError(Exception):
    def __init__(self, suffix: str):
        super().__init__(f"There is no loader for file extension {suffix}")


class ConfigLoaderError(Exception):
    def __init__(self, config_path: Path) -> None:
        super().__init__(f"There was a problem loading config file {config_path}")


def toml_load(path: PathLike) -> ConfigDict:
    """Load a TOML config file"""
    with open(path, "rb") as fobj:
        return toml_load_fobj(fobj)


def json_load(path: PathLike) -> ConfigDict:
    """Load a JSON config file"""
    with open(path, "rb") as fobj:
        return json.load(fobj)


_loaders: Dict[str, ConfigDictLoader] = {".toml": toml_load, ".json": json_load}
"""Mapping of config file extension to config file loader"""


if yaml:

    def yaml_load(path: PathLike) -> ConfigDict:
        """Load a YAML config file"""
        with open(path, "r") as fobj:
            return yaml.load(fobj, Loader=YAMLLoader)

    _loaders[".yaml"] = yaml_load


def update_loaders(new_loaders: Dict[str, ConfigDictLoader]):
    """Update the config file loaders dict"""
    global _loaders
    _loaders.update(new_loaders)


def load_config(config_path: Path) -> ConfigDict:
    try:
        loader = _loaders[config_path.suffix]
    except KeyError:
        raise NoLoaderError(config_path.suffix) from None
    try:
        return loader(config_path)
    except Exception as ex:
        raise ConfigLoaderError(config_path) from ex
