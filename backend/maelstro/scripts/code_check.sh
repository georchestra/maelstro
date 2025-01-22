#!/bin/bash

cd "$(dirname "$0")"/..

poetry run black --check . && \
poetry run mypy --strict . && \
poetry run pyflakes . && \
poetry run pylint .

! (( $? & 7 ))  # mask exit code for minor findings (refactor, convention, usage)
