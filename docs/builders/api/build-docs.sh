#!/usr/bin/env bash

set -e

export PROJ_PATH=$(realpath $(dirname $0)/../../..)
DOCS_PATH=$PROJ_PATH/docs/manual
SCRIPT_PATH=$PROJ_PATH/docs/builders/api
JSON_PATH=$PROJ_PATH/outputs/docs/api-json

mkdir -p $JSON_PATH

cd $PROJ_PATH

$SCRIPT_PATH/docstrings-to-json.py thirdparty.pparse.lib > $JSON_PATH/thirdparty.pparse.lib-api.json

cat <<END_OF_MD_HEADER >$DOCS_PATH/6-api-reference/6.2-pparse-lib-api.md
---
title: Pparse Lib API
first-section-number: "6.2"
---

## Pparse Library API

The public API of pparse.

END_OF_MD_HEADER

$SCRIPT_PATH/json-to-pandoc-md.py $JSON_PATH/thirdparty.pparse.lib-api.json \
  >> $DOCS_PATH/6-api-reference/6.2-pparse-lib-api.md