#!/bin/bash -li
# shellcheck disable=SC1091
set -e
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

. "$SCRIPTDIR/test_vers.sh"

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
      mypy ./ --always-true PYDANTIC_1 --cache-dir "$env_dir/.mypy_cache"
    else
      mypy ./ --always-false PYDANTIC_1 --cache-dir "$env_dir/.mypy_cache"
    fi
    deactivate
    log "--------DONE with $env_dir--------"
    echo -e "\n\n\n" >&2
}

for py_ver in "${PY_VERS[@]}"; do
  for pyd_ver in "${PYD_VERS[@]}"; do
    testbed_dir="$SCRIPTDIR/testenvs/py${py_ver}_pyd${pyd_ver}"
    test_in_env "$testbed_dir"
  done
done
