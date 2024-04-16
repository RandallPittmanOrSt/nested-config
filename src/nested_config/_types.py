"""_types.py - Type aliases and type-checking functions"""

import sys
from pathlib import Path
from typing import Any, Callable, Dict, Union

from typing_extensions import TypeAlias

ConfigDict: TypeAlias = Dict[str, Any]
PathLike: TypeAlias = Union[Path, str]
ConfigDictLoader: TypeAlias = Callable[[Path], ConfigDict]


if sys.version_info >= (3, 10):
    from types import UnionType

    UNION_TYPES = [Union, UnionType]
else:
    UNION_TYPES = [Union]
