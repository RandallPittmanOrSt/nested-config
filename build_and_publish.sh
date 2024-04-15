#!/bin/bash
SCRIPTNAME="$(basename "$0")"

die() {
  echo "$SCRIPTNAME Error: ${1:-}" >&2
  exit "${2:-1}"
}

REPO="${1:-testpypi}"
echo "Publishing to the $REPO repo."

REPO_UPPER="$(echo "$REPO" | tr '[:lower:]' '[:upper:]')"
# shellcheck disable=SC1091
. .env || die "No .env file. Create one that exports POETRY_PYPI_TOKEN_${REPO_UPPER} "

declare -n REPO_TOKEN_ENVVAR=POETRY_PYPI_TOKEN_${REPO_UPPER}
[ -z "${!REPO_TOKEN_ENVVAR}" ] && die "$REPO_TOKEN_ENVVAR was apparently not set in the .env file"
poetry build || die "Problem with build step"
poetry publish --repository "$REPO"
