from pathlib import Path
from typing import Dict, List, Optional

import pydantic
import pytest

from nested_config import pyd_obj_from_config

YAML_DIR = Path(__file__).parent / "yaml_files"
HOUSE_YAML_PATH = YAML_DIR / "house.yaml"
HOUSE_YAML_BAD_DIMPATH_PATH = YAML_DIR / "house_bad_dimpath.yaml"
HOUSE_YAML_LISTDIM_PATH = YAML_DIR / "house_listdim.yaml"
HOUSE_YAML_DICTDIM_PATH = YAML_DIR / "house_dictdim.yaml"
HOUSE_WITH_GARAGE_YAML_PATH = YAML_DIR / "house_with_garage.yaml"
HOUSE_DIMENSIONS = {"length": 40, "width": 20, "height": 10}
GARAGE_DIMENSIONS = {"length": 15, "width": 15, "height": 8}
GARAGE_NAME = "way out back"


class Dimensions(pydantic.BaseModel):
    length: int
    width: int
    height: int


class House(pydantic.BaseModel):
    name: str
    dimensions: Dimensions


class HouseMaybeDim(pydantic.BaseModel):
    name: str
    dimensions: Optional[Dimensions]


class HouseListDim(pydantic.BaseModel):
    name: str
    dimensions: List[Dimensions]


class HouseDictDim(pydantic.BaseModel):
    name: str
    dimensions: Dict[str, Dimensions]


class Garage(pydantic.BaseModel):
    name: str
    dimensions: Dimensions


class HouseWithGarage(pydantic.BaseModel):
    name: str
    dimensions: Dimensions
    garage: Optional[Garage]


def test_submodel_yaml():
    house = pyd_obj_from_config(HOUSE_YAML_PATH, House)
    assert house.dimensions == Dimensions(**HOUSE_DIMENSIONS)


def test_optional_submodel():
    house = pyd_obj_from_config(HOUSE_YAML_PATH, HouseMaybeDim)
    assert house.dimensions == Dimensions(**HOUSE_DIMENSIONS)


def test_submodel_list():
    house = pyd_obj_from_config(HOUSE_YAML_LISTDIM_PATH, HouseListDim)
    assert house.dimensions[0] == Dimensions(**HOUSE_DIMENSIONS)
    assert house.dimensions[1] == Dimensions(**GARAGE_DIMENSIONS)


def test_submodel_dict():
    house = pyd_obj_from_config(HOUSE_YAML_DICTDIM_PATH, HouseDictDim)
    assert house.dimensions["house"] == Dimensions(**HOUSE_DIMENSIONS)
    assert house.dimensions["garage"] == Dimensions(**GARAGE_DIMENSIONS)


def test_subsubmodel():
    house = pyd_obj_from_config(HOUSE_WITH_GARAGE_YAML_PATH, HouseWithGarage)
    assert house.dimensions == Dimensions(**HOUSE_DIMENSIONS)
    assert house.garage
    assert house.garage.name == GARAGE_NAME
    assert house.garage.dimensions == Dimensions(**GARAGE_DIMENSIONS)


def test_submodel_yaml_badpath():
    with pytest.raises(FileNotFoundError):
        pyd_obj_from_config(HOUSE_YAML_BAD_DIMPATH_PATH, House)
