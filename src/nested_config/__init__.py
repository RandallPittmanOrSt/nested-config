"""nested_config - Parse configuration files that include references to other
configuration files into single configuration objects. See README and help for
nested_config.expand_config().
"""

try:
    # Don't require pydantic
    from nested_config._pydantic import (
        BaseModel,
        validate_config,
    )
except ImportError:
    pass

from nested_config.expand import ConfigExpansionError, expand_config
from nested_config.loaders import (
    ConfigLoaderError,
    NoLoaderError,
    config_dict_loaders,
)
from nested_config.version import __version__
