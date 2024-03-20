import typing
from pathlib import Path
from typing import Any, Dict, Mapping, Protocol, Type

import pydantic
import rtoml
from typing_extensions import TypeGuard

from pydantic_plus._types import UNION_TYPES, PathLike, PydModelT


class HasAnnotation(Protocol):
    """Protocol will allow some Pydantic 2.0 compatibility down the road"""

    annotation: Type[Any]


def ispydmodel(klass, cls: Type[pydantic.BaseModel]) -> TypeGuard[Type[pydantic.BaseModel]]:
    """Exception-safe issubclass for pydantic BaseModel types"""
    try:
        return issubclass(klass, cls)
    except:  # NOSONAR
        return False


def ispydobj(obj, cls: Type[pydantic.BaseModel]) -> TypeGuard[pydantic.BaseModel]:
    """Exception-safe isinstance for pydantic BaseModel types"""
    try:
        return isinstance(obj, cls)
    except:  # NOSONAR
        return False


def obj_from_toml(toml_path: PathLike, model: Type[PydModelT], convert_strpaths=False) -> PydModelT:
    """Create a pydantic model object from a TOML file

    Parameters
    ----------
    toml_path
        Path to the TOML file
    model
        Pydantic model type (subclass of Pydantic BaseModel) to create from the parsed
        TOML file.
    convert_strpaths
        If True, every string value [a] in the dict from the parsed TOML file that
        corresponds to a Pydantic model field [b] in the base model will be interpreted as
        a path to another TOML file and an attempt will be made to parse that TOML file
        [a] and make it into an object of that [b] model type, and so on, recursively.

    Returns
    -------
    A 'model'-type object

    Raises
    -------
    rtoml.TomlParsingError
        TOML is not valid
    pydantic.ValidationError
        The data fields or types in the TOML file do not match the model
    """
    # ensure Path, otherwise rtoml will assume it's a TOML string
    toml_path = Path(toml_path)
    toml_obj = rtoml.load(toml_path)
    if convert_strpaths:
        _preparse_toml_obj(toml_obj, model.__fields__, toml_path)
    return pydantic.parse_obj_as(model, toml_obj)


def _preparse_toml_obj(
    tomlobj: Dict[str, Any], model_fields: Mapping[str, HasAnnotation], toml_path: Path
) -> None:
    """Convert a dict parsed from a TOML file according to the pydantic model_fields"""
    tomlobj = {k: _preparse_tomlval(v, model_fields[k].annotation, toml_path) for k, v in tomlobj.items()}


def _preparse_tomlval(field_value: Any, modelfield_annoation, toml_path: Path) -> Any:
    if not isinstance(field_value, (str, list, dict)):
        return field_value
    annotation = _normalize_optional_annotation(modelfield_annoation)
    if isinstance(field_value, str) and ispydmodel(annotation, pydantic.BaseModel):
        return _toml_strfield_to_pydo(field_value, annotation, toml_path)
    if (
        isinstance(field_value, list)
        and all(isinstance(v, str) for v in field_value)
        and (lv_annotation := _list_model_annotation(annotation))
    ):
        return [_preparse_tomlval(v, lv_annotation, toml_path) for v in field_value]
    if (
        isinstance(field_value, dict)
        and all(isinstance(v, str) for v in field_value.values())
        and (kv_annotation := _dict_annotation(annotation))
    ):
        return {k: _preparse_tomlval(v, kv_annotation, toml_path) for k, v in field_value.items()}

    # Default case
    return field_value


def _normalize_optional_annotation(annotation):
    """Convert a possibly Optional annotation to its underlying annotation"""
    annotation_origin = typing.get_origin(annotation)
    annotation_args = typing.get_args(annotation)
    if (
        annotation_origin in UNION_TYPES
        and ispydmodel(annotation_args[0], pydantic.BaseModel)
        and annotation_args[1] is type(None)
    ):
        return annotation_args[0]
    return annotation


def _list_model_annotation(annotation):
    """If annotation is a List annotation, return the internal annotation if and only if it is a (maybe
    optional) Pydantic model, otherwise return None."""
    annotation_origin = typing.get_origin(annotation)
    annotation_args = typing.get_args(annotation)
    if (
        annotation_origin is list
        and len(annotation_args) > 0
        and ispydmodel(annotation_args[0], pydantic.BaseModel)
    ):
        return annotation_args[0]
    return None


def _dict_annotation(annotation):
    """If annotation is a Dict annotation with arguments, return the value annotation if and only if it is a
    (maybe optional) Pydantic model, otherwise return None."""
    annotation_origin = typing.get_origin(annotation)
    annotation_args = typing.get_args(annotation)
    if (
        annotation_origin is dict
        and len(annotation_args) > 1
        and ispydmodel(annotation_args[1], pydantic.BaseModel)
    ):
        return annotation_args[1]
    return None


def _toml_strfield_to_pydo(
    field_value: str, field_model: Type[PydModelT], base_toml_path: Path
) -> PydModelT:
    """Converts a TOML string field to a pydantic object by assuming it's a path,
    possibly relative to base_toml_path"""
    # assume it's a path to a toml file
    field_toml_path = Path(field_value)
    if not field_toml_path.is_absolute():
        # Assume it's relative to the current toml file
        field_toml_path = field_toml_path.relative_to(base_toml_path.parent)
    return obj_from_toml(field_toml_path, field_model)
