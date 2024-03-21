from pathlib import Path
from typing import Dict, List, Optional

import pydantic
import pytest

import pydantic_plus

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


def test_submodel_toml():
    house = pydantic_plus.pydo_from_config(HOUSE_TOML_PATH, House, convert_strpaths=True)
    assert house.dimensions == Dimensions(**HOUSE_DIMENSIONS)


def test_optional_submodel():
    house = pydantic_plus.pydo_from_config(
        HOUSE_TOML_PATH, HouseMaybeDim, convert_strpaths=True
    )
    assert house.dimensions == Dimensions(**HOUSE_DIMENSIONS)


def test_submodel_list():
    house = pydantic_plus.pydo_from_config(
        HOUSE_TOML_LISTDIM_PATH, HouseListDim, convert_strpaths=True
    )
    assert house.dimensions[0] == Dimensions(**HOUSE_DIMENSIONS)
    assert house.dimensions[1] == Dimensions(**GARAGE_DIMENSIONS)


def test_submodel_dict():
    house = pydantic_plus.pydo_from_config(
        HOUSE_TOML_DICTDIM_PATH, HouseDictDim, convert_strpaths=True
    )
    assert house.dimensions["house"] == Dimensions(**HOUSE_DIMENSIONS)
    assert house.dimensions["garage"] == Dimensions(**GARAGE_DIMENSIONS)


def test_subsubmodel():
    house = pydantic_plus.pydo_from_config(
        HOUSE_WITH_GARAGE_TOML_PATH, HouseWithGarage, convert_strpaths=True
    )
    assert house.dimensions == Dimensions(**HOUSE_DIMENSIONS)
    assert house.garage
    assert house.garage.name == GARAGE_NAME
    assert house.garage.dimensions == Dimensions(**GARAGE_DIMENSIONS)


def test_submodel_toml_badpath():
    with pytest.raises(FileNotFoundError):
        pydantic_plus.pydo_from_config(
            HOUSE_TOML_BAD_DIMPATH_PATH, House, convert_strpaths=True
        )
