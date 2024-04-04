"""pydantic_plus - This package does two things:

1. It adds the ability to parse config files into Pydantic model instances, including
   config files that include string path references to other config files in place of
   sub-model instances.

       my_obj = pyd_obj_from_config("my_config.toml", MyConfigModel, loader=toml.load)

2. It adds PurePath, PurePosixPath, and PureWindowsPath validation and JSON-encoding to
   Pydantic v1 (these are already included in Pydantic 2.)
"""

from pydantic_plus._validators import (
    patch_pydantic_validators as _patch_pydantic_validators,
)
from pydantic_plus.base_model import BaseModel
from pydantic_plus.json import patch_pydantic_json_encoders
from pydantic_plus.parsing import ispydmodel, pyd_obj_from_config
from pydantic_plus.version import __version__

# We always patch the validators, but in the future this may be made optional
_patch_pydantic_validators()
