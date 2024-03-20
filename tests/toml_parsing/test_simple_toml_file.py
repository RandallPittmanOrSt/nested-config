"""Test reading in a simple TOML file into pydanic models"""

from pathlib import Path

import pydantic
import pydantic_plus

BASIC_POINT_FILE = Path(__file__).parent / "point.toml"


class Point(pydantic_plus.BaseModel):
    name: str
    x: int
    y: int


class Point2(pydantic.BaseModel):
    name: str
    x: int
    y: int

POINT_DATA = {"name": "home", "x": 3, "y": 2}

def test_basic_point_file():
    """Test creating a Point with the from_toml method of pydantic_plus.BaseModel"""
    assert Point.from_toml(BASIC_POINT_FILE) == Point(**POINT_DATA)


def test_basic_point_file2():
    """Test creating a Point2 with pydantic_plus.obj_from_toml"""
    assert pydantic_plus.obj_from_toml(BASIC_POINT_FILE, Point2) == Point2(**POINT_DATA)
