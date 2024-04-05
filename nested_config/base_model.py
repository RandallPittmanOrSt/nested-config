"""base_model.py

Pydantic BaseModel extended a bit:
  - PurePosixPath json encoding and validation
  - from_toml and from_tomls classmethods
"""

import sys
from pathlib import Path
from typing import Type

import pydantic

if sys.version_info < (3, 11):
    from tomli import load as toml_load_fobj
else:
    from tomllib import load as toml_load_fobj

from nested_config import parsing
from nested_config._compat import parse_obj
from nested_config._types import ConfigDict, PathLike, PydModelT


def _toml_load(path: PathLike) -> ConfigDict:
    with open(path, "rb") as fobj:
        return toml_load_fobj(fobj)


class BaseModel(pydantic.BaseModel):
    """Extends pydantic.BaseModel with conversion from TOML and incluedes json encoding of
    PurePosixPath"""

    @classmethod
    def from_toml(
        cls: Type[PydModelT], toml_path: PathLike, convert_strpaths=False
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
        rtoml.TomlParsingError
            TOML is not valid
        pydantic.ValidationError
            The data fields or types in the TOML file do not match the model
        """
        if convert_strpaths:
            return parsing.pyd_obj_from_config(toml_path, cls, loader=_toml_load)
        else:
            config_dict = _toml_load(Path(toml_path))
            return parse_obj(cls, config_dict)

    @classmethod
    def from_tomls(cls: Type[PydModelT], toml_str: str) -> PydModelT:
        """Create pydantic model from a TOML string

        Parameters
        ----------
        toml_str
            TOML-formatted data structure

        Raises
        -------
        TomlParsingError
            TOML is not valid
        ValidationError
            The data in the TOML file does not match the model
        """
        return parse_obj(cls, _toml_load(toml_str))
