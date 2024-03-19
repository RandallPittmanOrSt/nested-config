from pathlib import Path
from typing import TypeVar, Union

import pydantic
from typing_extensions import TypeAlias

PathLike: TypeAlias = Union[Path, str]

PydModelT = TypeVar("PydModelT", bound=pydantic.BaseModel)
