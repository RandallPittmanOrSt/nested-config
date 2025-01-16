"""nested_config - Parse configuration files that include references to other
configuration files into single configuration objects. See README and help for
nested_config.expand_config().
"""

try:
    # Don't require pydantic
    from ._pydantic import (
        BaseModel,
        validate_config,
    )
except ImportError:
    pass

from .expand import ConfigExpansionError, expand_config
from .loaders import (
    ConfigLoaderError,
    NoLoaderError,
    config_dict_loaders,
)
from .version import __version__
