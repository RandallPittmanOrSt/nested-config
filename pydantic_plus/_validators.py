from pathlib import PurePath, PurePosixPath, PureWindowsPath
from typing import Any, Type, TypeVar

import pydantic
import pydantic.validators

PathT = TypeVar("PathT", bound=PurePath)


def _path_validator(v: Any, type: Type[PathT]) -> PathT:
    """Attempt to convert a value to a PurePosixPath"""
    if isinstance(v, type):
        return v
    try:
        return type(v)
    except TypeError:
        raise pydantic.PathError


def pure_path_validator(v: Any):
    return _path_validator(v, type=PurePath)


def pure_posix_path_validator(v: Any):
    return _path_validator(v, type=PurePosixPath)


def pure_windows_path_validator(v: Any):
    return _path_validator(v, type=PureWindowsPath)


def patch_pydantic_validators():
    pydantic.validators._VALIDATORS.extend(
        [
            (PurePosixPath, [pure_posix_path_validator]),
            (PureWindowsPath, [pure_windows_path_validator]),
            (PurePath, [pure_path_validator]),  # last because others are more specific
        ]
    )
