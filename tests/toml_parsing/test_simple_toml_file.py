"""Test reading in a simple TOML file into pydanic models"""

from pathlib import Path

import pydantic
import rtoml

import pydantic_plus

TOML_PATH = Path(__file__).parent / "simple_house.toml"


class House(pydantic_plus.BaseModel):
    name: str
    length: int
    width: int


class House2(pydantic.BaseModel):
    name: str
    length: int
    width: int


HOUSE_DATA = {"name": "home", "length": 30, "width": 20}


def test_basic_point_file():
    """Test creating a Point with the from_toml method of pydantic_plus.BaseModel"""
    assert House.from_toml(TOML_PATH) == House(**HOUSE_DATA)


def test_basic_point_file2():
    """Test creating a Point2 with pydantic_plus.obj_from_toml"""
    assert pydantic_plus.pyd_obj_from_config(
        TOML_PATH, House2, loader=rtoml.load
    ) == House2(**HOUSE_DATA)
