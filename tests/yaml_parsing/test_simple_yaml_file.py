"""Test reading in a simple YAML file into pydanic models"""

from pathlib import Path

import pydantic
import yaml

import nested_config
from nested_config._types import PathLike, ConfigDict

YAML_PATH = Path(__file__).parent / "yaml_files" / "simple_house.yaml"


def _yaml_load(path: PathLike) -> ConfigDict:
    with open(path, "rb") as fobj:
        return yaml.load(fobj, Loader=yaml.Loader)


class House(pydantic.BaseModel):
    name: str
    length: int
    width: int


HOUSE_DATA = {"name": "home", "length": 30, "width": 20}


def test_base_house_file():
    """Test creating a House with nested_config.pyd_obj_from_config"""
    house2 = nested_config.pyd_obj_from_config(YAML_PATH, House, loader=_yaml_load)
    assert house2 == House(**HOUSE_DATA)
