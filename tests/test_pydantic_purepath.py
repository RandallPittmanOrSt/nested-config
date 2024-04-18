"""Test that we can just patch pydantic with nested_config rather than using the
nested_config base model"""

import json
import os
from pathlib import PurePath, PurePosixPath, PureWindowsPath

import pydantic

# import Pydantic 1/2 compat fns. Also importing nested_config auto-patches pydantic
from nested_config._pydantic import dump_json, model_validate

PURE_POSIX_PATH = "/some/pure/path"
PURE_WINDOWS_PATH = "C:\\some\\pure\\path"
NATIVE_PURE_PATH = PURE_WINDOWS_PATH if os.name == "nt" else PURE_POSIX_PATH


class ModelWithPurePath(pydantic.BaseModel):
    p: PurePath


class ModelWithPurePosixPath(pydantic.BaseModel):
    p: PurePosixPath


class ModelWithPureWindowsPath(pydantic.BaseModel):
    p: PureWindowsPath


def test_can_validate_pp():
    data = {"p": NATIVE_PURE_PATH}
    m = model_validate(ModelWithPurePath, data)
    assert (
        m.p == PureWindowsPath(data["p"]) if os.name == "nt" else PurePosixPath(data["p"])
    )


def test_can_validate_ppp():
    data = {"p": PURE_POSIX_PATH}
    m = model_validate(ModelWithPurePosixPath, data)
    assert m.p == PurePosixPath(data["p"])


def test_can_validate_pwp():
    data = {"p": PURE_WINDOWS_PATH}
    m = model_validate(ModelWithPureWindowsPath, data)
    assert m.p == PureWindowsPath(data["p"])


def test_can_serialize_pp():
    p = PurePath(NATIVE_PURE_PATH)
    m = ModelWithPurePath(p=p)
    json_model = dump_json(m)
    assert json.loads(json_model) == {"p": str(p)}


def test_can_serialize_ppp():
    p = PurePosixPath(PURE_POSIX_PATH)
    m = ModelWithPurePosixPath(p=p)
    json_model = dump_json(m)
    assert json.loads(json_model) == {"p": str(p)}


def test_can_serialize_pw():
    p = PureWindowsPath(PURE_WINDOWS_PATH)
    m = ModelWithPureWindowsPath(p=p)
    json_model = dump_json(m)
    assert json.loads(json_model) == {"p": str(p)}
