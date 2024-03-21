from rtoml import TomlParsingError

from pydantic_plus._validators import (
    patch_pydantic_validators as _patch_pydantic_validators,
)
from pydantic_plus.base_model import BaseModel
from pydantic_plus.json import patch_pydantic_json_encoders
from pydantic_plus.parsing import ispydmodel, pydo_from_toml
from pydantic_plus.version import __version__

# We always patch the validators, but in the future this may be made optional
_patch_pydantic_validators()
