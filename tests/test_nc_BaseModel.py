"""Test reading in a simple TOML file into pydanic models"""

from pathlib import Path

import nested_config

TOML_PATH = Path(__file__).parent / "toml_files" / "simple_house.toml"
YAML_PATH = Path(__file__).parent / "yaml_files" / "simple_house.yaml"


class House(nested_config.BaseModel):
    name: str
    length: int
    width: int


HOUSE_DATA = {"name": "home", "length": 30, "width": 20}


def test_basic_house_file():
    """Test creating a House with the from_toml method of nested_config.BaseModel"""
    assert House.from_config(TOML_PATH) == House(**HOUSE_DATA)
    assert House.from_config(YAML_PATH) == House(**HOUSE_DATA)
