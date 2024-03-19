from pathlib import Path
from typing import Type

import pydantic
import rtoml

from pydantic_plus._types import PathLike, PydModelT


def obj_from_toml(toml_path: PathLike, model: Type[PydModelT]) -> PydModelT:
    """Create a pydantic model object from a TOML file

    Parameters
    ----------
    toml_path
        Path to the TOML file

    Raises
    -------
    TomlParsingError
        TOML is not valid
    ValidationError
        The data in the TOML file does not match the model
    """
    # ensure Path, otherwise rtoml will assume it's a TOML string
    toml_path = Path(toml_path)
    toml_obj = rtoml.load(toml_path)
    return pydantic.parse_obj_as(model, toml_obj)
