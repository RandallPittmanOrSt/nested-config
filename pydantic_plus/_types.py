from pathlib import Path
from typing import TypeVar, Union

from pydantic import BaseModel as PydanticBaseModel
from typing_extensions import TypeAlias

PathLike: TypeAlias = Union[Path, str]

PydModelT = TypeVar("PydModelT", bound="PydanticBaseModel")
