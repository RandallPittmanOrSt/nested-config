"""_pyd_compat.py - Functions and types to assist with Pydantic 1/2 compatibility"""

from pathlib import PurePath, PurePosixPath, PureWindowsPath
from typing import Any, Dict, Optional, Type, TypeVar

import pydantic
import pydantic.errors
import pydantic.fields
import pydantic.json
import pydantic.validators
from setuptools._vendor.packaging.version import Version  # type: ignore
from typing_extensions import TypeAlias, TypeGuard

from nested_config._types import PathLike
from nested_config.expand import expand_config

PathT = TypeVar("PathT", bound=PurePath)
PydModelT = TypeVar("PydModelT", bound=pydantic.BaseModel)
PYDANTIC_1 = Version(pydantic.VERSION) < Version("2.0")


if PYDANTIC_1:
    FieldInfo_: TypeAlias = pydantic.fields.ModelField
else:
    FieldInfo_: TypeAlias = pydantic.fields.FieldInfo
ModelFields: TypeAlias = Dict[str, FieldInfo_]


def ispydmodel(klass, cls: Type[PydModelT]) -> TypeGuard[Type[PydModelT]]:
    """Exception-safe issubclass for pydantic BaseModel types"""
    return isinstance(klass, type) and issubclass(klass, cls)


def validate_config(
    config_path: PathLike,
    model: Type[PydModelT],
    *,
    default_suffix: Optional[str] = None,
) -> PydModelT:
    """Load a config file into a Pydantic model. The config file may contain string paths
    where nested models would be expected. These are preparsed into their respective
    models.

    If paths to nested models are relative, they are assumed to be relative to the path of
    their parent config file.

    Input
    -----
    config_path
        A string or pathlib.Path to the config file to parse
    model
        The Pydantic model to use for creating the config object
    default_suffix
        If there is no loader for the config file suffix (or the config file has no
        suffix) try to load the config with the loader specified by this extension, e.g.
        '.toml' or '.yml'
    Returns
    -------
    A Pydantic object of the type specified by the model input.

    Raises
    ------
    NoLoaderError
        No loader is available for the config file extension
    ConfigLoaderError
        There was a problem loading a config file with its loader
    pydantic.ValidationError
        The data fields or types in the file do not match the model.

    """
    config_dict = expand_config(config_path, model, default_suffix=default_suffix)
    # Create and validate the config object
    return parse_obj(model, config_dict)


def parse_obj(model: Type[PydModelT], obj: Any) -> PydModelT:
    if PYDANTIC_1:
        return model.parse_obj(obj)
    else:
        return model.model_validate(obj)


def dump_json(model: pydantic.BaseModel) -> str:
    """Compatibility of json dump function for testing"""
    if PYDANTIC_1:
        return model.json()
    else:
        return model.model_dump_json()


def patch_pydantic_json_encoders():
    if PYDANTIC_1:
        # These are already in pydantic 2+
        pydantic.json.ENCODERS_BY_TYPE[PurePath] = str


def _path_validator(v: Any, type: Type[PathT]) -> PathT:
    """Attempt to convert a value to a PurePosixPath"""
    if isinstance(v, type):
        return v
    try:
        return type(v)
    except TypeError:
        # n.b. this error only exists in Pydantic < 2.0
        raise pydantic.errors.PathError from None


def pure_path_validator(v: Any):
    return _path_validator(v, type=PurePath)


def pure_posix_path_validator(v: Any):
    return _path_validator(v, type=PurePosixPath)


def pure_windows_path_validator(v: Any):
    return _path_validator(v, type=PureWindowsPath)


def patch_pydantic_validators():
    if PYDANTIC_1:
        # These are already included in pydantic 2+
        pydantic.validators._VALIDATORS.extend(
            [
                (PurePosixPath, [pure_posix_path_validator]),
                (PureWindowsPath, [pure_windows_path_validator]),
                (
                    PurePath,
                    [pure_path_validator],
                ),  # last because others are more specific
            ]
        )
