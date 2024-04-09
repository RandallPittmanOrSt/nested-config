"""Test reading in a simple TOML file into pydanic models"""

from pathlib import Path

import pydantic

import nested_config

TOML_PATH = Path(__file__).parent / "toml_files" / "simple_house.toml"
YAML_PATH = Path(__file__).parent / "yaml_files" / "simple_house.yaml"


class House(nested_config.BaseModel):
    name: str
    length: int
    width: int


class House2(pydantic.BaseModel):
    name: str
    length: int
    width: int


HOUSE_DATA = {"name": "home", "length": 30, "width": 20}


def test_basic_house_file():
    """Test creating a House with the from_toml method of nested_config.BaseModel"""
    assert House.from_config(TOML_PATH) == House(**HOUSE_DATA)
    assert House.from_config(YAML_PATH) == House(**HOUSE_DATA)


def test_basic_house_file2():
    """Test creating a House2 with nested_config.obj_from_toml"""
    house2 = nested_config.validate_config(TOML_PATH, House2)
    assert house2 == House2(**HOUSE_DATA)
    house2_yaml = nested_config.validate_config(YAML_PATH, House2)
    assert house2_yaml == House2(**HOUSE_DATA)
