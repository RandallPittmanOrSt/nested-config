"""Test reading in a simple YAML file into pydanic models"""

from pathlib import Path

import pydantic

import nested_config

YAML_PATH = Path(__file__).parent / "yaml_files" / "simple_house.yaml"


class House(pydantic.BaseModel):
    name: str
    length: int
    width: int


HOUSE_DATA = {"name": "home", "length": 30, "width": 20}


def test_base_house_file():
    """Test creating a House with nested_config.pyd_obj_from_config"""
    house2 = nested_config.pyd_obj_from_config(YAML_PATH, House)
    assert house2 == House(**HOUSE_DATA)
