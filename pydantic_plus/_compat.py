from typing import Any, Dict, Optional, Protocol, Type

from typing_extensions import TypeAlias

import pydantic
import pydantic.fields
from setuptools._vendor.packaging.version import Version

from pydantic_plus._types import PydModelT

PYDANTIC_1 = Version(pydantic.__version__) < Version("2.0")


class HasAnnotation(Protocol):
    """Protocol will allow some Pydantic 2.0 compatibility down the road"""

    annotation: Optional[Type[Any]]


if PYDANTIC_1:
    ModelFields: TypeAlias = Dict[str, pydantic.fields.ModelField]
else:
    ModelFields: TypeAlias = Dict[str, pydantic.fields.FieldInfo]


def model_fields(model: Type[pydantic.BaseModel]) -> ModelFields:
    if PYDANTIC_1:
        return model.__fields__
    else:
        return model.model_fields


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
