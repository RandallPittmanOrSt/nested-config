"""_validators.py - For Pydantic 1.8-1.10, extends the built-in validators to include
PurePath & subclasses"""

from pathlib import PurePath, PurePosixPath, PureWindowsPath
from typing import Any, Type, TypeVar

import pydantic
import pydantic.errors
import pydantic.validators

from nested_config._compat import PYDANTIC_1

PathT = TypeVar("PathT", bound=PurePath)


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
