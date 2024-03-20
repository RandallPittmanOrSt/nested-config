"""Test that we can validate strings as PurePaths and also json-serialize them using
pydantic_plus."""

import os
from pathlib import PurePath, PurePosixPath, PureWindowsPath

import pydantic_plus

PURE_POSIX_PATH = "/some/pure/path"
PURE_WINDOWS_PATH = "C:\\some\\pure\\path"
NATIVE_PURE_PATH = PURE_WINDOWS_PATH if os.name == "nt" else PURE_POSIX_PATH


class ModelWithPurePath(pydantic_plus.BaseModel):
    p: PurePath


class ModelWithPurePosixPath(pydantic_plus.BaseModel):
    p: PurePosixPath


class ModelWithPureWindowsPath(pydantic_plus.BaseModel):
    p: PureWindowsPath


def test_can_validate_pp():
    data = {"p": NATIVE_PURE_PATH}
    m = ModelWithPurePath.parse_obj(data)
    assert (
        m.p == PureWindowsPath(data["p"]) if os.name == "nt" else PurePosixPath(data["p"])
    )


def test_can_validate_ppp():
    data = {"p": PURE_POSIX_PATH}
    m = ModelWithPurePosixPath.parse_obj(data)
    assert m.p == PurePosixPath(data["p"])


def test_can_validate_pwp():
    data = {"p": PURE_WINDOWS_PATH}
    m = ModelWithPureWindowsPath.parse_obj(data)
    assert m.p == PureWindowsPath(data["p"])


def test_can_serialize_pp():
    p = PurePath(NATIVE_PURE_PATH)
    m = ModelWithPurePath(p=p)
    json_model = m.json()
    assert json_model == f'{{"p": "{p}"}}'


def test_can_serialize_ppp():
    p = PurePosixPath(PURE_POSIX_PATH)
    m = ModelWithPurePosixPath(p=p)
    json_model = m.json()
    assert json_model == f'{{"p": "{p}"}}'


def test_can_serialize_pw():
    p = PureWindowsPath(PURE_WINDOWS_PATH)
    m = ModelWithPureWindowsPath(p=p)
    json_model = m.json()
    # json replaces backslashes with double-backslashes
    json_pwp = PURE_WINDOWS_PATH.replace("\\", "\\\\")
    assert json_model == f'{{"p": "{json_pwp}"}}'
