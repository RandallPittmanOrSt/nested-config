from pathlib import Path
from typing import Dict, List, Optional

import pytest
from nested_config import expand_config

TOML_DIR = Path(__file__).parent / "toml_files"
YAML_DIR = Path(__file__).parent / "yaml_files"

HOUSE_TOML_PATH = TOML_DIR / "house.toml"
HOUSE_TOML_BAD_DIMPATH_PATH = TOML_DIR / "house_bad_dimpath.toml"
HOUSE_TOML_LISTDIM_PATH = TOML_DIR / "house_listdim.toml"
HOUSE_TOML_DICTDIM_PATH = TOML_DIR / "house_dictdim.toml"
HOUSE_WITH_GARAGE_TOML_PATH = TOML_DIR / "house_with_garage.toml"
NEIGHBORHOOD_TOML_PATH = TOML_DIR / "neighborhood.toml"

HOUSE_DIMENSIONS = {"length": 40, "width": 20, "height": 10}
GARAGE_DIMENSIONS = {"length": 15, "width": 15, "height": 8}
GARAGE_NAME = "way out back"


def _test_paths(toml_path: Path) -> List[Path]:
    return [toml_path, YAML_DIR / f"{toml_path.stem}.yaml"]


class Dimensions:
    length: int
    width: int
    height: int


class House:
    name: str
    dimensions: Dimensions


class HouseMaybeDim:
    name: str
    dimensions: Optional[Dimensions]


class HouseListDim:
    name: str
    dimensions: List[Dimensions]


class HouseDictDim:
    name: str
    dimensions: Dict[str, Dimensions]


class Garage:
    name: str
    dimensions: Dimensions


class HouseWithGarage(House):
    garage: Optional[Garage]


class Neighborhood:
    name: str
    houses: List[HouseWithGarage]


@pytest.mark.parametrize("config_path", _test_paths(HOUSE_TOML_PATH))
def test_submodel(config_path):
    house = expand_config(config_path, House)
    assert house["dimensions"] == HOUSE_DIMENSIONS


@pytest.mark.parametrize("config_path", _test_paths(HOUSE_TOML_PATH))
def test_optional_submodel(config_path):
    house = expand_config(config_path, HouseMaybeDim)
    assert house["dimensions"] == HOUSE_DIMENSIONS


@pytest.mark.parametrize("config_path", _test_paths(HOUSE_TOML_LISTDIM_PATH))
def test_submodel_list(config_path):
    house = expand_config(config_path, HouseListDim)
    assert house["dimensions"][0] == HOUSE_DIMENSIONS
    assert house["dimensions"][1] == GARAGE_DIMENSIONS


@pytest.mark.parametrize("config_path", _test_paths(HOUSE_TOML_DICTDIM_PATH))
def test_submodel_dict(config_path):
    house = expand_config(config_path, HouseDictDim)
    assert house["dimensions"]["house"] == HOUSE_DIMENSIONS
    assert house["dimensions"]["garage"] == GARAGE_DIMENSIONS


@pytest.mark.parametrize("config_path", _test_paths(HOUSE_WITH_GARAGE_TOML_PATH))
def test_subsubmodel(config_path):
    house = expand_config(config_path, HouseWithGarage)
    assert house["dimensions"] == HOUSE_DIMENSIONS
    assert house["garage"]
    assert house["garage"]["name"] == GARAGE_NAME
    assert house["garage"]["dimensions"] == GARAGE_DIMENSIONS


@pytest.mark.parametrize("config_path", _test_paths(HOUSE_TOML_BAD_DIMPATH_PATH))
def test_submodel_toml_badpath(config_path):
    with pytest.raises(FileNotFoundError):
        expand_config(HOUSE_TOML_BAD_DIMPATH_PATH, House)


NEIGHBORHOOD = {
    "name": "Beverly Hills",
    "houses": [
        {
            "name": "Mom's house",
            "dimensions": {"length": 40, "width": 20, "height": 10},
            "garage": {
                "name": "way out back",
                "dimensions": {"length": 15, "width": 15, "height": 8},
            },
        },
        {
            "name": "my house",
            "dimensions": {"length": 50, "width": 30, "height": 20},
            "garage": {
                "name": "my garage",
                "dimensions": {"length": 15, "width": 15, "height": 8},
            },
        },
    ],
}


def test_neighborhood():
    """Complicated case with some nested models manually defined, some defined by a path"""
    assert expand_config(NEIGHBORHOOD_TOML_PATH, Neighborhood) == NEIGHBORHOOD
