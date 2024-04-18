"""_pyd_compat.py - Functions and types to assist with Pydantic 1/2 compatibility"""

import warnings
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath
from typing import Any, Optional, Type, TypeVar

import pydantic
import pydantic.errors
import pydantic.fields
import pydantic.json
import pydantic.validators
from setuptools._vendor.packaging.version import Version  # type: ignore
from typing_extensions import Unpack

from nested_config._types import PathLike
from nested_config.expand import expand_config
from nested_config.loaders import load_config

PathT = TypeVar("PathT", bound=PurePath)
PydModelT = TypeVar("PydModelT", bound=pydantic.BaseModel)
PYDANTIC_1 = Version(pydantic.VERSION) < Version("2.0")


def api_deprecation(api_name):
    warnings.warn(
        f"{api_name} is deprecated as of nested_config v2.1.0 and will be removed in"
        " v3.0.0",
        DeprecationWarning,
        stacklevel=2,
    )


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
    api_deprecation("nested_config.validate_config")
    config_dict = expand_config(config_path, model, default_suffix=default_suffix)
    # Create and validate the config object
    return model_validate(model, config_dict)


def model_validate(model: Type[PydModelT], obj: Any) -> PydModelT:
    """Pydantic 1/2 compatibility wrapper for model.model_validate"""
    if PYDANTIC_1:
        return model.parse_obj(obj)
    else:
        return model.model_validate(obj)


def dump_json(model: pydantic.BaseModel) -> str:
    """Pydantic 1/2 compatibility wrapper for model.model_dump_json"""
    if PYDANTIC_1:
        return model.json()
    else:
        return model.model_dump_json()


def patch_pydantic_json_encoders():
    """Add PurePath encoder for JSON in Pydantic < 2.0"""
    if PYDANTIC_1:
        api_deprecation("nested_config.patch_pydantic_json_encoders")
        # These are already in pydantic 2+
        pydantic.json.ENCODERS_BY_TYPE[PurePath] = str


def _path_validator(v: Any, type: Type[PathT]) -> PathT:
    """Attempt to convert a value to a PurePath"""
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
    """Add Pure*Path validators to Pydantic < 2.0"""
    if PYDANTIC_1:
        api_deprecation("nested_config.patch_pydantic_validators")
        # These are already included in pydantic 2+
        pydantic.validators._VALIDATORS.extend(
            [
                (PurePosixPath, [pure_posix_path_validator]),
                (PureWindowsPath, [pure_windows_path_validator]),
                (PurePath, [pure_path_validator]),  # last b/c others are more specific
            ]
        )


# Always patch pydantic
patch_pydantic_json_encoders()
patch_pydantic_validators()


class BaseModel(pydantic.BaseModel):
    """Extends pydantic.BaseModel with from_config classmethod to load a config file into
    the model."""

    if PYDANTIC_1:

        def __init_subclass__(cls) -> None:
            api_deprecation("nested_config.BaseModel")
            return super().__init_subclass__()
    else:

        def __init_subclass__(cls, **kwargs: Unpack[pydantic.ConfigDict]):
            api_deprecation("nested_config.BaseModel")
            return super().__init_subclass__(**kwargs)

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
