"""_compat.py - Functions and types to assist with Pydantic 1/2 compatibility"""

from typing import Any, Dict, Optional, Protocol, Type

import pydantic
import pydantic.fields
from setuptools._vendor.packaging.version import Version  # type: ignore
from typing_extensions import TypeAlias

from nested_config._types import PydModelT

PYDANTIC_1 = Version(pydantic.VERSION) < Version("2.0")


class HasAnnotation(Protocol):
    """Protocol will allow some Pydantic 2.0 compatibility down the road"""

    annotation: Optional[Type[Any]]


if PYDANTIC_1:
    ModelFields: TypeAlias = Dict[str, pydantic.fields.ModelField]
else:
    ModelFields: TypeAlias = Dict[str, pydantic.fields.FieldInfo]


def get_field_annotation(model: Type[pydantic.BaseModel], field_name: str):
    # "annotation" exists in pydantic 1.10, but not 1.8 or 1.9
    field = get_model_fields(model)[field_name]
    return field.outer_type_ if PYDANTIC_1 else field.annotation


def get_model_fields(model: Type[pydantic.BaseModel]) -> ModelFields:
    return model.__fields__ if PYDANTIC_1 else model.model_fields


def parse_obj(model: Type[PydModelT], obj: Any) -> PydModelT:
    return model.parse_obj(obj) if PYDANTIC_1 else model.model_validate(obj)


def dump_json(model: pydantic.BaseModel) -> str:
    """Compatibility of json dump function for testing"""
    return model.json() if PYDANTIC_1 else model.model_dump_json()
