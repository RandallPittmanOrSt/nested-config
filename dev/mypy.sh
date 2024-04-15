#!/bin/bash
pydantic_version=$(pip show pydantic | grep '^Version:' | cut -d' ' -f2)
pydantic_version_major=$(echo "$pydantic_version" | cut -d'.' -f1)
declare -a mypy_args
if [ "$pydantic_version_major" -lt 2 ]; then
  mypy_args+=("--always-true" "PYDANTIC_1")
else
  mypy_args+=("--always-false" "PYDANTIC_1")
fi

mypy "${mypy_args[@]}" ./