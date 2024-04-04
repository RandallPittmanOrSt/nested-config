"""_types.py - Type aliases and type-checking functions"""

import sys
from pathlib import Path
from typing import TypeVar, Union

import pydantic
from typing_extensions import TypeAlias

PathLike: TypeAlias = Union[Path, str]

PydModelT = TypeVar("PydModelT", bound=pydantic.BaseModel)


if sys.version_info >= (3, 10):
    from types import UnionType

    UNION_TYPES = [Union, UnionType]
else:
    UNION_TYPES = [Union]
