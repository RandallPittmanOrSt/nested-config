"""loaders.py - Manage config file loaders"""

import contextlib
import json
import sys
from pathlib import Path
from typing import Dict, Optional

if sys.version_info < (3, 11):
    from tomli import load as toml_load_fobj
else:
    from tomllib import load as toml_load_fobj

from nested_config._types import ConfigDict, ConfigDictLoader, PathLike


class NoLoaderError(Exception):
    def __init__(self, suffix: str, default_suffix: Optional[str]):
        msg_tail = ""
        if default_suffix:
            msg_tail = f" nor a loader for default suffix {default_suffix}"
        super().__init__(f"There is no loader for file extension {suffix}{msg_tail}.")


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


config_dict_loaders: Dict[str, ConfigDictLoader] = {
    ".toml": toml_load,
    ".json": json_load,
}
"""Mapping of config file extension to config file loader"""

# Add YAML loader, if available
with contextlib.suppress(ImportError):
    import yaml

    def yaml_load(path: PathLike) -> ConfigDict:
        """Load a YAML config file (safely)"""
        with open(path, "r") as fobj:
            return yaml.safe_load(fobj)

    config_dict_loaders[".yaml"] = yaml_load
    config_dict_loaders[".yml"] = yaml_load


def _get_loader(config_path: Path, default_suffix: Optional[str] = None):
    """Get the loader for the specified suffix, or a loader from default suffix"""
    try:
        try:
            return config_dict_loaders[config_path.suffix]
        except KeyError:
            if default_suffix:
                return config_dict_loaders[default_suffix]
            raise
    except KeyError:
        raise NoLoaderError(config_path.suffix, default_suffix) from None


def load_config(config_path: Path, default_suffix: Optional[str] = None) -> ConfigDict:
    """Select a loader based on the suffix (extension) of the config file and try to load
    the config using that loader. E.g. for .toml, use the TOML loader.

    Inputs
    ------
    config_path
        Path to the config file

    Returns
    -------
    ConfigDict
        A mapping of the data stored in the config file

    Raises
    ------
    NoLoaderError (via _get_loader)
        No loader could be found for the suffix (or default suffix, if provided)
    ConfigLoaderError
        There was an error running the loader (e.g. in tomllib or yaml or json)
    """
    loader = _get_loader(config_path, default_suffix)
    try:
        return loader(config_path)
    except Exception as ex:
        raise ConfigLoaderError(config_path) from ex
