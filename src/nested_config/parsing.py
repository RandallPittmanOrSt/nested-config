"""parsing.py - Functions to parse config files (e.g. TOML) into Pydantic model instances,
possibly with nested models specified by string paths."""

import typing
from pathlib import Path
from typing import Optional, Type

import pydantic

from nested_config import _compat
from nested_config._types import (
    UNION_TYPES,
    ConfigDict,
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
    config_dict = _preparse_config_dict(config_dict, model, config_path)
    # Create and validate the config object
    return _compat.parse_obj(model, config_dict)


def _preparse_config_dict(
    config_dict: ConfigDict, model: Type[pydantic.BaseModel], config_path: Path
):
    return {
        key: _preparse_config_value(
            value, _compat.get_modelfield_annotation(model, key), config_path
        )
        for key, value in config_dict.items()
    }


def _preparse_config_value(field_value, field_annotation, config_path: Path):
    """Check if a model field contains a path to another model and parse it accordingly"""
    # If the annotation is optional, get the enclosed annotation
    field_annotation = _get_optional_ann(field_annotation)
    # ###
    # N cases:
    # 1. Config value is not a string, list, or dict
    # 2. Config value is a dict, model expects a model
    # 3. Config value is a string, model expects a model
    # 4. Config value is a list, model expects a list of some type
    # 5. Config value is a dict, model expects a dict with values of a particular model
    #    type
    # 6. A string, list, or dict that doesn't match cases 2-5
    # ###

    # 1.
    if not isinstance(field_value, (str, list, dict)):
        return field_value
    # 2.
    if isinstance(field_value, dict) and ispydmodel(field_annotation, pydantic.BaseModel):
        return _preparse_config_dict(field_value, field_annotation, config_path)
    # 3.
    if isinstance(field_value, str) and ispydmodel(field_annotation, pydantic.BaseModel):
        return _parse_path_str_into_pydmodel(field_value, field_annotation, config_path)
    # 4.
    if isinstance(field_value, list) and (
        listval_annotation := _get_list_value_ann(field_annotation)
    ):
        return [
            _preparse_config_value(li, listval_annotation, config_path)
            for li in field_value
        ]
    # 5.
    if isinstance(field_value, dict) and (
        dictval_annotation := _get_dict_value_ann(field_annotation)
    ):
        return {
            key: _preparse_config_value(value, dictval_annotation, config_path)
            for key, value in field_value.items()
        }
    # 6.
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
    if annotation_origin in UNION_TYPES and annotation_args[1] is type(None):
        return annotation_args[0]
    return annotation


def _get_list_value_ann(annotation):
    """Get the internal annotation of a typed list, if any. Otherwise return None."""
    annotation_origin = typing.get_origin(annotation)
    annotation_args = typing.get_args(annotation)
    if annotation_origin is list and len(annotation_args) > 0:
        return annotation_args[0]
    return None


def _get_dict_value_ann(annotation):
    """Get the internal annotation of a dict's value type, if any. Otherwise return
    None."""
    annotation_origin = typing.get_origin(annotation)
    annotation_args = typing.get_args(annotation)
    if annotation_origin is dict and len(annotation_args) > 1:
        return annotation_args[1]
    return None
