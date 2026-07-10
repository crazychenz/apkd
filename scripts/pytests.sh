#!/usr/bin/env bash

export PROJ_PATH=$(realpath $(dirname $0)/..)
cd ${PROJ_PATH}

if [ -z "$1" ]; then
  pytest --log-cli-level=INFO tests/pytests
else
  pytest --log-cli-level=INFO $@
fi
