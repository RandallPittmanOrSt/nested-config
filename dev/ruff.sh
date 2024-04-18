#!/bin/bash
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(realpath -s "$SCRIPTDIR/..")"
cd "$PROJECT_ROOT" || { echo "Couldn't cd to project root" >&2 ; exit 1 ; }

ruff format
ruff check --select I --fix
ruff check
