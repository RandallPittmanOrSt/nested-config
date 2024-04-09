"""parsing.py - Functions to parse config files (e.g. TOML) into Pydantic model instances,
possibly with nested models specified by string paths."""

import typing
from pathlib import Path
from typing import Optional, Type

import pydantic

from nested_config import _compat
from nested_config._types import (
    UNION_TYPES,
    PathLike,
    PydModelT,
    ispydmodel,
)
from nested_config.loaders import load_config, set_default_loader


def validate_config(
    config_path: PathLike,
    model: Type[PydModelT],
    *,
    default_suffix: Optional[str] = None,
) -> PydModelT:
    """Load a config file into a Pydantic model. The config file may contain string paths
    where nested models would be expected. These are preparsed into their respective
    models.

    If paths to nested models are relative, they are assumed to be relative to the path of
    their parent config file.

    Input
    -----
    config_path
        A string or pathlib.Path to the config file to parse
    model
        The Pydantic model to use for creating the config object
    default_suffix
        If there is no loader for the config file suffix (or the config file has no
        suffix) try to load the config with the loader specified by this extension, e.g.
        '.toml' or '.yml'
    Returns
    -------
    A Pydantic object of the type specified by the model input.

    Raises
    ------
    NoLoaderError
        No loader is available for the config file extension
    ConfigLoaderError
        There was a problem loading a config file with its loader
    pydantic.ValidationError
        The data fields or types in the file do not match the model.

    """
    if default_suffix:
        set_default_loader(default_suffix)
    # Input arg coercion
    config_path = Path(config_path)
    # Get the config dict and the model fields
    config_dict = load_config(config_path)
    # preparse the config (possibly loading nested configs)
    config_dict = {
        key: _preparse_config_value(
            value, _compat.get_field_annotation(model, key), config_path
        )
        for key, value in config_dict.items()
    }
    # Create and validate the config object
    return _compat.parse_obj(model, config_dict)


def _preparse_config_value(field_value, field_annotation, config_path: Path):
    """Check if a model field contains a path to another model and parse it accordingly"""
    # If the annotation is optional, get the enclosed annotation
    field_annotation = _get_optional_ann(field_annotation)
    # ###
    # Five cases:
    # 1. Not a string, list, or dict
    # 2. String field to be parsed into a model instance
    # 3. List of strings field where each string is a model instance
    # 4. Dict with string values where each string is a model instance
    # 5. A string, list, or dict that doesn't match cases 2-4
    # ###

    # 1.
    if not isinstance(field_value, (str, list, dict)):
        return field_value
    # 2.
    if isinstance(field_value, str) and ispydmodel(field_annotation, pydantic.BaseModel):
        return _parse_path_str_into_pydmodel(field_value, field_annotation, config_path)
    # 3.
    if (
        isinstance(field_value, list)
        and all(isinstance(li, str) for li in field_value)
        and (listval_annotation := _get_list_value_ann(field_annotation))
    ):
        return [
            _parse_path_str_into_pydmodel(li, listval_annotation, config_path)
            for li in field_value
        ]
    # 4.
    if (
        isinstance(field_value, dict)
        and all(isinstance(vi, str) for vi in field_value.values())
        and (dictval_annotation := _get_dict_value_ann(field_annotation))
    ):
        return {
            key: _parse_path_str_into_pydmodel(value, dictval_annotation, config_path)
            for key, value in field_value.items()
        }
    # 5.
    return field_value


def _parse_path_str_into_pydmodel(
    path_str: str, model: Type[PydModelT], parent_path: Path
) -> PydModelT:
    """Convert a path string to a path (possibly relative to a parent config path) and
    create an instance of a Pydantic model"""
    path = Path(path_str)
    if not path.is_absolute():
        # Assume it's relative to the parent config path
        path = parent_path.parent / path
    if not path.is_file():
        raise FileNotFoundError(
            f"Config file '{parent_path}' contains a path to another config file"
            f" '{path_str}' that could not be found."
        )
    return validate_config(path, model)


def _get_optional_ann(annotation):
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


def _get_list_value_ann(annotation):
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


def _get_dict_value_ann(annotation):
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
