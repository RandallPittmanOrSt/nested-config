#!/bin/bash -li
set -e

log() {
    echo "$*" >&2
}

die() {
    log "${1:-}"
    exit "${2-1}"
}

[ -d test_envs/py38_pyd1/ ] || die "Create a venv .venv38_pyd1 with Python 3.8 and Pydantic 1.10+"
[ -d test_envs/py311_pyd2/ ] || die "Create a venv .venv311_pyd2 with Python 3.11 and Pydantic 2.0+"

log "-------------------------------------------"
log "Using venv with Python 3.8 and Pydantic < 2"
log "-------------------------------------------"
. test_envs/py38_pyd1/.venv/bin/activate
log "--Running mypy--"
log ""
log ""
mypy --always-true PYDANTIC_1 ./
log "--Running pytest"
pytest ./
deactivate

log ""
log ""

log "---------------------------------------------"
log "Using venv with Python 3.11 and Pydantic >= 2"
log "---------------------------------------------"
. test_envs/py311_pyd2/.venv/bin/activate
log "--Running mypy"
mypy --always-false PYDANTIC_1 ./
log ""
log ""
log "--Running pytest"
pytest ./
deactivate
