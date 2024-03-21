from pathlib import Path
from typing import Any, Dict

import rtoml
from typing_extensions import TypeAlias

from pydantic_plus._types import PathLike

ConfigObj: TypeAlias = Dict[str, Any]


def load_config_file(config_file: PathLike) -> ConfigObj:
    return rtoml.load(Path(config_file))


def load_config_text(config_text: str) -> ConfigObj:
    return rtoml.loads(config_text)
