from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from nested_config import expand_config


class Dimensions:
    length: int
    width: int
    height: int


class House:
    name: str
    dimensions: Dimensions


class Garage:
    name: str
    dimensions: Dimensions


class HouseWithGarage(House):
    garage: Optional[Garage]


class Neighborhood:
    name: str
    houses: List[HouseWithGarage]


HOUSE_DIMENSIONS = {"length": 40, "width": 20, "height": 10}


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
    """Complicated case with some nested models manually defined, some defined by a path,
    also inheritance"""
    NEIGHBORHOOD_TOML_PATH = Path(__file__).parent / "toml_files/neighborhood.toml"
    assert expand_config(NEIGHBORHOOD_TOML_PATH, Neighborhood) == NEIGHBORHOOD
