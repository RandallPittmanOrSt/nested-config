"""parsing.py - Functions to parse config files (e.g. TOML) into Pydantic model instances,
possibly with nested models specified by string paths."""

import functools
import inspect
import typing
from pathlib import Path
from typing import Any, Dict, Optional

from nested_config._types import (
    UNION_TYPES,
    ConfigDict,
    PathLike,
)
from nested_config.loaders import load_config


def expand_config(
    config_path: PathLike,
    model: type,
    *,
    default_suffix: Optional[str] = None,
) -> ConfigDict:
    expander = ConfigExpander(default_suffix=default_suffix)
    return expander.expand(config_path, model)


class ConfigExpansionError(RuntimeError):
    pass


@functools.lru_cache
def get_model_annotations(model: type) -> Dict[str, Any]:
    """Get the aggregated annotations of all members of a model"""
    annotations: Dict[str, Any] = {}
    for cls in inspect.getmro(model)[::-1]:
        annotations.update(cls.__dict__.get("__annotations__", {}))
    return annotations


def get_modelfield_annotation(model: type, field_name: str):
    """Try to get the field annotation for some type, e.g. a dataclass or Pydantic
    model

    Inputs
    ------
    model
        The template class from which we want field annotations.
    field_name
        Name of the field to get

    Returns
    -------
    The type annotation of the chosen field

    Raises
    ------
    ConfigExpansionError
        There is no field of that name in the specified model
    """

    try:
        return get_model_annotations(model)[field_name]
    except KeyError:
        raise ConfigExpansionError(
            f"Model type {model} does not have a field named {field_name}"
        ) from None


def is_model(val: Any) -> bool:
    return hasattr(val, "__dict__") and "__annotations__" in val.__dict__


class ConfigExpander:
    def __init__(self, *, default_suffix: Optional[str] = None):
        self.default_suffix = default_suffix

    def expand(self, config_path: PathLike, model: type) -> ConfigDict:
        config_path = Path(config_path)
        config_dict = load_config(config_path, self.default_suffix)
        return self._preparse_config_dict(config_dict, model, config_path)

    def _preparse_config_dict(
        self, config_dict: ConfigDict, model: type, config_path: Path
    ):
        return {
            key: self._preparse_config_value(
                value, get_modelfield_annotation(model, key), config_path
            )
            for key, value in config_dict.items()
        }

    def _preparse_config_value(
        self, field_value: str, field_annotation: Any, config_path: Path
    ):
        """Check if a model field contains a path to another model and parse it
        accordingly"""
        # If the annotation is optional, get the enclosed annotation
        field_annotation = _get_optional_ann(field_annotation)
        # ###
        # N cases:
        # 1. Config value is not a string, list, or dict
        # 2. Config value is a dict, model expects a model
        # 3. Config value is a string, model expects a model
        # 4. Config value is a list, model expects a list of some type
        # 5. Config value is a dict, model expects a dict with values of some type
        # 6. A string, list, or dict that doesn't match cases 2-5
        # ###

        # 1.
        if not isinstance(field_value, (str, list, dict)):
            return field_value
        # 2.
        if isinstance(field_value, dict) and is_model(field_annotation):
            return self._preparse_config_dict(field_value, field_annotation, config_path)
        # 3.
        if isinstance(field_value, str) and is_model(field_annotation):
            return self._expand_path_str_into_model(
                field_value, field_annotation, config_path
            )
        # 4.
        if isinstance(field_value, list) and (
            listval_annotation := _get_list_value_ann(field_annotation)
        ):
            return [
                self._preparse_config_value(li, listval_annotation, config_path)
                for li in field_value
            ]
        # 5.
        if isinstance(field_value, dict) and (
            dictval_annotation := _get_dict_value_ann(field_annotation)
        ):
            return {
                key: self._preparse_config_value(value, dictval_annotation, config_path)
                for key, value in field_value.items()
            }
        # 6.
        return field_value

    def _expand_path_str_into_model(
        self, path_str: str, model: type, parent_path: Path
    ) -> ConfigDict:
        """Convert a path string to a path (possibly relative to a parent config path) and
        use expand() to load that config file, possibly expanding further sub-config
        files based on the model type."""
        path = Path(path_str)
        if not path.is_absolute():
            # Assume it's relative to the parent config path
            path = parent_path.parent / path
        if not path.is_file():
            raise FileNotFoundError(
                f"Config file '{parent_path}' contains a path to another config file"
                f" '{path_str}' that could not be found."
            )
        return self.expand(path, model)


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
