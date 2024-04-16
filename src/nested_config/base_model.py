"""base_model.py

Pydantic BaseModel extended a bit:
  - PurePosixPath json encoding and validation
  - from_toml and from_tomls classmethods
"""

from pathlib import Path
from typing import Type

import pydantic

from nested_config._pydantic import PydModelT, model_validate, validate_config
from nested_config._types import PathLike
from nested_config.loaders import load_config


class BaseModel(pydantic.BaseModel):
    """Extends pydantic.BaseModel with from_config classmethod to load a config file into
    the model."""

    @classmethod
    def from_config(
        cls: Type[PydModelT], config_path: PathLike, convert_strpaths=True
    ) -> PydModelT:
        """Create Pydantic model from a config file

        Parameters
        ----------
        config_path
            Path to the config file
        convert_strpaths
            If True, every string value [a] in the dict from the parsed config file that
            corresponds to a Pydantic model field [b] in the base model will be
            interpreted as a path to another config file and an attempt will be made to
            parse that config file [a] and make it into an object of that [b] model type,
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
        config_path = Path(config_path)
        if convert_strpaths:
            return validate_config(config_path, cls)
        # otherwise just load the config as-is
        config_dict = load_config(config_path)
        return model_validate(cls, config_dict)
