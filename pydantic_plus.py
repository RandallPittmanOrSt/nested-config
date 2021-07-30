"""pydantic_plus.py

Pydantic BaseModel extended a bit:
  - PurePosixPath json encoding and validation
  - from_toml and from_tomls classmethods

"""

from pathlib import Path, PurePosixPath
from typing import Any, Type, TypeVar

import rtoml
from pydantic import BaseModel as PydanticBaseModel
from pydantic.validators import _VALIDATORS
from rtoml import TomlParsingError

__all__ = ["BaseModel", "PurePosixPathError", "TomlParsingError"]

__version__ = "1.1.3"

PydModel = TypeVar("PydModel", bound="BaseModel")


class BaseModel(PydanticBaseModel):
    """Extends pydantic BaseModel with conversion from TOML and incluedes json encoding of PurePosixPath"""

    class Config:
        json_encoders = {PurePosixPath: lambda p: str(p)}

    @classmethod
    def from_toml(cls: Type[PydModel], toml_path: Path) -> PydModel:
        """Create pydantic model from a TOML file

        Parameters
        ----------
        toml_path
            Path to the TOML file

        Raises
        -------
        TomlParsingError
            TOML is not valid
        ValidationError
            The data in the TOML file does not match the model
        """
        toml_path = Path(toml_path)  # ensure Path for rtoml, else assumed to be TOML string
        return cls.parse_obj(rtoml.load(toml_path))

    @classmethod
    def from_tomls(cls: Type[PydModel], toml_str: str) -> PydModel:
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


_VALIDATORS.append((PurePosixPath, [validate_pure_posix_path]))
