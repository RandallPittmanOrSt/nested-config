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
    FieldInfo_: TypeAlias = pydantic.fields.ModelField
else:
    FieldInfo_: TypeAlias = pydantic.fields.FieldInfo
ModelFields: TypeAlias = Dict[str, FieldInfo_]


def get_modelfield_annotation(model: Type[pydantic.BaseModel], field_name: str):
    # "annotation" exists in pydantic 1.10, but not 1.8 or 1.9
    field = get_model_fields(model)[field_name]
    return get_field_annotation(field)


def get_field_annotation(field: FieldInfo_):
    # "annotation" exists in pydantic 1.10, but not 1.8 or 1.9
    if PYDANTIC_1:
        return field.outer_type_
    else:
        return field.annotation


def get_model_fields(model: Type[pydantic.BaseModel]) -> ModelFields:
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
