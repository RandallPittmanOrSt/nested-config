"""base_model.py

Pydantic BaseModel extended a bit:
  - PurePosixPath json encoding and validation
  - from_toml and from_tomls classmethods
"""

from pathlib import Path
from typing import Type

import pydantic

from nested_config import parsing
from nested_config._compat import parse_obj
from nested_config._types import PathLike, PydModelT
from nested_config.loaders import load_config


class BaseModel(pydantic.BaseModel):
    """Extends pydantic.BaseModel with from_config classmethod to load a config file into
    the model."""

    @classmethod
    def from_config(
        cls: Type[PydModelT], toml_path: PathLike, convert_strpaths=True
    ) -> PydModelT:
        """Create Pydantic model from a TOML file

        Parameters
        ----------
        toml_path
            Path to the TOML file
        convert_strpaths
            If True, every string value [a] in the dict from the parsed TOML file that
            corresponds to a Pydantic model field [b] in the base model will be
            interpreted as a path to another TOML file and an attempt will be made to
            parse that TOML file [a] and make it into an object of that [b] model type,
            and so on, recursively.

        Returns
        -------
        An object of this class

        Raises
        -------
        NoLoaderError
            No loader is available for the config file extension
        ConfigLoaderError
            There was a problem loading a config file with its loader
        pydantic.ValidationError
            The data fields or types in the file do not match the model.
        """
        toml_path = Path(toml_path)
        if convert_strpaths:
            return parsing.validate_config(toml_path, cls)
        # otherwise just load the config as-is
        config_dict = load_config(toml_path)
        return parse_obj(cls, config_dict)
