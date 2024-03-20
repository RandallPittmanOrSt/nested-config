from pathlib import PurePath

import pydantic.json


def patch_pydantic_json_encoders():
    pydantic.json.ENCODERS_BY_TYPE = {**pydantic.json.ENCODERS_BY_TYPE, PurePath: str}
