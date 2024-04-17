#!/bin/bash -li
set -e
# shellcheck disable=SC1091
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

log() {
    echo "$*" >&2
}

die() {
    log "${1:-}"
    exit "${2-1}"
}

test_in_env() {
    local env_dir pyd_verstr pyd_majorver
    env_dir="$1"
    log "--------Testing in $env_dir--------"
    pyd_verstr="$(basename "$env_dir"| cut -d_ -f2)"
    pyd_majorver="${pyd_verstr:3:1}"
    . "$env_dir/bin/activate"
    cd "$SCRIPTDIR/.." || die "couldn't cd"
    log "----pytest----"
    pytest
    log "----mypy----"
    if [ "$pyd_majorver" -eq 1 ]; then
      mypy ./ --always-true PYDANTIC_1
    else
      mypy ./ --always-false PYDANTIC_1
    fi
    deactivate
    log "--------DONE with $env_dir--------"
}

for tb_dir in "$SCRIPTDIR"/testbeds/*; do
  test_in_env "$tb_dir"
done
