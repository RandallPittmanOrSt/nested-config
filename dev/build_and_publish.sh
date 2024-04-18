#!/bin/bash
# shellcheck disable=SC1091
SCRIPTNAME="$(basename "$0")"
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(realpath -s "$SCRIPTDIR/..")"

log() {
  local msg="${1:-}"
  local loglevel="${2:-INFO}"
  echo "$SCRIPTNAME $loglevel: $msg" >&2
}

die() {
  log "${1:-}" ERROR
  exit "${2:-1}"
}

REPO="${1:-testpypi}"
log "----Publishing to the $REPO repo.----"

REPO_UPPER="$(echo "$REPO" | tr '[:lower:]' '[:upper:]')"

cd "$PROJECT_ROOT" || die "Couldn't cd to project root"
. .env 2>/dev/null || die "No .env file. Create one that exports POETRY_PYPI_TOKEN_${REPO_UPPER} "

declare -n REPO_TOKEN_ENVVAR=POETRY_PYPI_TOKEN_${REPO_UPPER}
[ -z "$REPO_TOKEN_ENVVAR" ] && die "${!REPO_TOKEN_ENVVAR} was apparently not set in the .env file"
poetry build || die "Problem with build step"
if [ "$REPO" = "pypi" ]; then
  poetry publish
else
  poetry publish --repository "$REPO"
fi
