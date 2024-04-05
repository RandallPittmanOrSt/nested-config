"""_types.py - Type aliases and type-checking functions"""

import sys
from pathlib import Path
from typing import Any, Callable, Dict, Type, TypeVar, Union

import pydantic
from typing_extensions import TypeAlias, TypeGuard

ConfigDict: TypeAlias = Dict[str, Any]
PathLike: TypeAlias = Union[Path, str]
PydModelT = TypeVar("PydModelT", bound=pydantic.BaseModel)
ConfigDictLoader: TypeAlias = Callable[[Path], ConfigDict]


if sys.version_info >= (3, 10):
    from types import UnionType

    UNION_TYPES = [Union, UnionType]
else:
    UNION_TYPES = [Union]


def ispydmodel(klass, cls: Type[PydModelT]) -> TypeGuard[Type[PydModelT]]:
    """Exception-safe issubclass for pydantic BaseModel types"""
    return isinstance(klass, type) and issubclass(klass, cls)
