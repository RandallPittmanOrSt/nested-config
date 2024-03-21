from pathlib import Path
from typing import Any, Dict

import rtoml
from typing_extensions import TypeAlias

from pydantic_plus._types import PathLike

TomlObj: TypeAlias = Dict[str, Any]


def load_toml_file(toml_file: PathLike) -> TomlObj:
    return rtoml.load(Path(toml_file))


def load_toml_text(toml_text: str) -> TomlObj:
    return rtoml.loads(toml_text)
