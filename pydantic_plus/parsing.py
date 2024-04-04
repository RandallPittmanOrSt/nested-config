"""parsing.py - Functions to parse config files (e.g. TOML) into Pydantic model instances,
possibly with nested models specified by string paths."""

import typing
from pathlib import Path
from typing import Any, Type

import pydantic
from typing_extensions import TypeGuard

from pydantic_plus._compat import ModelFields, model_fields, parse_obj
from pydantic_plus._config import ConfigObj, load_config_file
from pydantic_plus._types import UNION_TYPES, PathLike, PydModelT


def ispydmodel(klass, cls: Type[PydModelT]) -> TypeGuard[Type[PydModelT]]:
    """Exception-safe issubclass for pydantic BaseModel types"""
    return isinstance(klass, type) and issubclass(klass, cls)


def pyd_obj_from_config(
) -> PydModelT:
    """Create a pydantic model object from a TOML file

    Parameters
    ----------
    config_path
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

    """
    config_path = Path(config_path)
    config_obj = load_config_file(config_path)
    if convert_strpaths:
        config_obj = _preparse_config_obj(config_obj, model_fields(model), config_path)
    return parse_obj(model, config_obj)


def _preparse_config_obj(
    config_obj: ConfigObj, model_fields: ModelFields, config_path: Path
) -> ConfigObj:
    """Convert a dict parsed from a TOML file according to the pydantic model_fields"""
    return {
        k: _preparse_configval(v, model_fields[k].annotation, config_path)
        for k, v in config_obj.items()
    }


def _preparse_configval(field_value: Any, modelfield_annotation, config_path: Path) -> Any:
    if not isinstance(field_value, (str, list, dict)):
        return field_value
    annotation = _normalize_optional_annotation(modelfield_annotation)
    if isinstance(field_value, str) and ispydmodel(annotation, pydantic.BaseModel):
        return _config_strfield_to_pydo(field_value, annotation, config_path)
    if (
        isinstance(field_value, list)
        and all(isinstance(v, str) for v in field_value)
        and (lv_annotation := _list_model_annotation(annotation))
    ):
        return [_preparse_configval(v, lv_annotation, config_path) for v in field_value]
    if (
        isinstance(field_value, dict)
        and all(isinstance(v, str) for v in field_value.values())
        and (kv_annotation := _dict_annotation(annotation))
    ):
        return {
            k: _preparse_configval(v, kv_annotation, config_path)
            for k, v in field_value.items()
        }

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
    """If annotation is a List annotation, return the internal annotation if and only if
    it is a (maybe optional) Pydantic model, otherwise return None."""
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
    """If annotation is a Dict annotation with arguments, return the value annotation if
    and only if it is a (maybe optional) Pydantic model, otherwise return None."""
    annotation_origin = typing.get_origin(annotation)
    annotation_args = typing.get_args(annotation)
    if (
        annotation_origin is dict
        and len(annotation_args) > 1
        and ispydmodel(annotation_args[1], pydantic.BaseModel)
    ):
        return annotation_args[1]
    return None


def _config_strfield_to_pydo(
    field_value: str, field_model: Type[PydModelT], base_config_path: Path
) -> PydModelT:
    """Converts a TOML string field to a pydantic object by assuming it's a path,
    possibly relative to base_config_path"""
    # assume it's a path to a config file
    field_config_path = Path(field_value)
    if not field_config_path.is_absolute():
        # Assume it's relative to the current config file
        field_config_path = base_config_path.parent / field_config_path
    return pydo_from_config(field_config_path, field_model, convert_strpaths=True)
