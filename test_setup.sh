#!/bin/bash -li
set -e

export POETRY_VIRTUALENVS_PREFER_ACTIVE_PYTHON=true

ENV_BASE=test_envs/py38_pyd1/
if [ ! -d $ENV_BASE/.venv ]; then
    mkdir -p $ENV_BASE && pushd $ENV_BASE
    pyenv shell 3.8
    python -m venv .venv
    . .venv/bin/activate
    pip install -U pip
    poetry install
    pip uninstall pydantic pydantic_core
    pip install "pydantic<2.0"
    deactivate
    popd
fi

ENV_BASE=test_envs/py311_pyd2/
if [ ! -d "$VENV" ]; then
    mkdir -p $ENV_BASE && pushd $ENV_BASE
    pyenv shell 3.11
    python -m venv .venv
    . .venv/bin/activate
    pip install -U pip
    poetry install
    deactivate
    popd
fi
