#!/usr/bin/env bash

# pip install griffe

set -e

export PROJ_PATH=$(realpath $(dirname $0)/../../..)

cd $PROJ_PATH/docs/manual/api-build

./build-api-docs.py