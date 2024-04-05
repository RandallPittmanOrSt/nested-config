"""Test reading in a simple TOML file into pydanic models"""

from pathlib import Path

import pydantic

import nested_config
from nested_config.base_model import _toml_load

TOML_PATH = Path(__file__).parent / "toml_files" / "simple_house.toml"


class House(nested_config.BaseModel):
    name: str
    length: int
    width: int


class House2(pydantic.BaseModel):
    name: str
    length: int
    width: int


HOUSE_DATA = {"name": "home", "length": 30, "width": 20}


def test_basic_point_file():
    """Test creating a Point with the from_toml method of nested_config.BaseModel"""
    assert House.from_toml(TOML_PATH) == House(**HOUSE_DATA)


def test_basic_point_file2():
    """Test creating a Point2 with nested_config.obj_from_toml"""
    assert nested_config.pyd_obj_from_config(
        TOML_PATH, House2, loader=_toml_load
    ) == House2(**HOUSE_DATA)
