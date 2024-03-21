from pathlib import PurePath

import pydantic.json

from pydantic_plus._compat import PYDANTIC_1


def patch_pydantic_json_encoders():
    if PYDANTIC_1:
        # These are already in pydantic 2+
        pydantic.json.ENCODERS_BY_TYPE = {**pydantic.json.ENCODERS_BY_TYPE, PurePath: str}
