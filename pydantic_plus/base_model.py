"""base_model.py

Pydantic BaseModel extended a bit:
  - PurePosixPath json encoding and validation
  - from_toml and from_tomls classmethods

"""

from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Type

import pydantic
import rtoml
from pydantic.validators import _VALIDATORS

from pydantic_plus import parsing
from pydantic_plus._types import PathLike, PydModelT


class BaseModel(pydantic.BaseModel):
    """Extends pydantic.BaseModel with conversion from TOML and incluedes json encoding of
    PurePosixPath"""

    class Config:
        json_encoders = {PurePosixPath: str, PureWindowsPath: str}

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
        return parsing.obj_from_toml(toml_path, cls, convert_strpaths)

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
        return cls.parse_obj(rtoml.loads(toml_str))


def validate_pure_posix_path(v: Any) -> PurePosixPath:
    """Attempt to convert a value to a PurePosixPath"""
    return PurePosixPath(v)


def validate_pure_windows_path(v: Any) -> PureWindowsPath:
    """Attempt to convert a value to a PurePosixPath"""
    return PureWindowsPath(v)


_VALIDATORS.extend(
    [
        (PurePosixPath, [validate_pure_posix_path]),
        (PureWindowsPath, [validate_pure_windows_path]),
    ]
)
