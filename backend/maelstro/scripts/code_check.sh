#!/bin/bash

cd "$(dirname "$0")"/..

black --check . && \
mypy --strict . && \
pyflakes . && \
pylint --disable=R,C --extension-pkg-allow-list=saxonche maelstro
