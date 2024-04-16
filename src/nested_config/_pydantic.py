"""_pyd_compat.py - Functions and types to assist with Pydantic 1/2 compatibility"""

from pathlib import PurePath, PurePosixPath, PureWindowsPath
from typing import Any, Dict, Optional, Protocol, Type, TypeVar

import pydantic
import pydantic.errors
import pydantic.fields
import pydantic.json
import pydantic.validators
from setuptools._vendor.packaging.version import Version  # type: ignore
from typing_extensions import TypeAlias

from nested_config._types import PydModelT

PathT = TypeVar("PathT", bound=PurePath)
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


def patch_pydantic_json_encoders():
    if PYDANTIC_1:
        # These are already in pydantic 2+
        pydantic.json.ENCODERS_BY_TYPE[PurePath] = str


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
