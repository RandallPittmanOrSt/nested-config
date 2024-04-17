#!/bin/bash -li
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# SCRIPTNAME=$(basename "${BASH_SOURCE[0]}")
readonly SCRIPTDIR
set -e

envs_dir="$SCRIPTDIR/testbeds"

export POETRY_VIRTUALENVS_PREFER_ACTIVE_PYTHON=true

PY_VERS=(3.8 3.9 3.10 3.11 3.12)
PYD_VERS=(1.8 1.10 2.7)

die() {
    echo "$SCRIPTNAME Error: ${1:-}" >&2
    exit "${2:-1}"
}

setup_venv() {
    local py_ver="$1"
    local pyd_ver="$2"
    local env_dir="$envs_dir/py${py_ver}_pyd${pyd_ver}"
    mkdir -p "$env_dir"
    pyenv shell "$py_ver"
    python -m venv "$env_dir" || die "Coudln't create venv"
    # shellcheck disable=SC1091
    . "$env_dir/bin/activate"
    pip install -U pip || die "Couldn't update pip"
    pip install "pydantic==$pyd_ver" pyyaml pytest mypy types-pyyaml || die "couldn't install pydantic or pyyaml"
    pip install -e "$SCRIPTDIR/../" || die "Couldn't install nested-config"
    deactivate
}

for py_ver in "${PY_VERS[@]}"; do
  for pyd_ver in "${PYD_VERS[@]}"; do
    setup_venv "$py_ver" "$pyd_ver"
  done
done
