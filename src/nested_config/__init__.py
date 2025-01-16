"""nested_config - Parse configuration files that include references to other
configuration files into single configuration objects. See README and help for
nested_config.expand_config().
"""

# N.b. redundant aliases export names to type checkers, see
# <https://github.com/microsoft/pyright/blob/main/docs/typed-libraries.md#library-interface>
try:
    # Don't require pydantic
    from nested_config._pydantic import BaseModel as BaseModel
    from nested_config._pydantic import validate_config as validate_config
except ImportError:
    pass

from nested_config.expand import ConfigExpansionError as ConfigExpansionError
from nested_config.expand import expand_config as expand_config
from nested_config.loaders import ConfigLoaderError as ConfigLoaderError
from nested_config.loaders import NoLoaderError as NoLoaderError
from nested_config.loaders import config_dict_loaders as config_dict_loaders
from nested_config.version import __version__ as __version__
