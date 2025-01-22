#!/bin/bash

cd "$(dirname "$0")"/..

black --check . && \
mypy --strict . && \
pyflakes . && \
pylint .

! (( $? & 7 ))  # mask exit code for minor findings (refactor, convention, usage)
