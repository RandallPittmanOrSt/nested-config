"""nested_config - This package does two things:

1. It adds the ability to parse config files into Pydantic model instances, including
   config files that include string path references to other config files in place of
   sub-model instances.

       my_obj = validate_config("my_config.toml", MyConfigModel, loader=toml.load)

2. It adds PurePath, PurePosixPath, and PureWindowsPath validation and JSON-encoding to
   Pydantic v1 (these are already included in Pydantic 2.)
"""

from nested_config._validators import (
    patch_pydantic_validators as _patch_pydantic_validators,
)
from nested_config.base_model import BaseModel
from nested_config.json import (
    patch_pydantic_json_encoders as _patch_pydantic_json_encoders,
)
from nested_config.loaders import (
    ConfigLoaderError,
    NoLoaderError,
    config_dict_loaders,
    set_default_loader,
)
from nested_config.parsing import ispydmodel, validate_config
from nested_config.version import __version__

# We always patch the validators, but in the future this may be made optional
_patch_pydantic_validators()
_patch_pydantic_json_encoders()
