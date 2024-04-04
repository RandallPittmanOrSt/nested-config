from functools import partial
from pathlib import Path
from typing import Dict, List, Optional

import pydantic
import pytest
import rtoml

from pydantic_plus import pyd_obj_from_config

SCRIPTDIR = Path(__file__).parent
HOUSE_TOML_PATH = SCRIPTDIR / "house.toml"
HOUSE_TOML_BAD_DIMPATH_PATH = SCRIPTDIR / "house_bad_dimpath.toml"
HOUSE_TOML_LISTDIM_PATH = SCRIPTDIR / "house_listdim.toml"
HOUSE_TOML_DICTDIM_PATH = SCRIPTDIR / "house_dictdim.toml"
HOUSE_WITH_GARAGE_TOML_PATH = SCRIPTDIR / "house_with_garage.toml"
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


pyd_obj_from_toml = partial(pyd_obj_from_config, loader=rtoml.load)


def test_submodel_toml():
    house = pyd_obj_from_toml(HOUSE_TOML_PATH, House)
    assert house.dimensions == Dimensions(**HOUSE_DIMENSIONS)


def test_optional_submodel():
    house = pyd_obj_from_toml(HOUSE_TOML_PATH, HouseMaybeDim)
    assert house.dimensions == Dimensions(**HOUSE_DIMENSIONS)


def test_submodel_list():
    house = pyd_obj_from_toml(HOUSE_TOML_LISTDIM_PATH, HouseListDim)
    assert house.dimensions[0] == Dimensions(**HOUSE_DIMENSIONS)
    assert house.dimensions[1] == Dimensions(**GARAGE_DIMENSIONS)


def test_submodel_dict():
    house = pyd_obj_from_toml(HOUSE_TOML_DICTDIM_PATH, HouseDictDim)
    assert house.dimensions["house"] == Dimensions(**HOUSE_DIMENSIONS)
    assert house.dimensions["garage"] == Dimensions(**GARAGE_DIMENSIONS)


def test_subsubmodel():
    house = pyd_obj_from_toml(HOUSE_WITH_GARAGE_TOML_PATH, HouseWithGarage)
    assert house.dimensions == Dimensions(**HOUSE_DIMENSIONS)
    assert house.garage
    assert house.garage.name == GARAGE_NAME
    assert house.garage.dimensions == Dimensions(**GARAGE_DIMENSIONS)


def test_submodel_toml_badpath():
    with pytest.raises(FileNotFoundError):
        pyd_obj_from_toml(HOUSE_TOML_BAD_DIMPATH_PATH, House)
