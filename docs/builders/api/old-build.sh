#!/usr/bin/env bash

# pip install pydoc-markdown

set -e

pydoc-markdown

FILES=(
  api-output/api/pparse-framework/parse.md
)

OUT=manual/5-api-reference/5.x-python-api.md
> "$OUT"
echo '<!-- AUTO GENERATED FILE, DO NOT EDIT --><!-- AUTO GENERATED FILE, DO NOT EDIT --><!-- AUTO GENERATED FILE, DO NOT EDIT --><!-- AUTO GENERATED FILE, DO NOT EDIT --><!-- AUTO GENERATED FILE, DO NOT EDIT --><!-- AUTO GENERATED FILE, DO NOT EDIT --><!-- AUTO GENERATED FILE, DO NOT EDIT --><!-- AUTO GENERATED FILE, DO NOT EDIT --><!-- AUTO GENERATED FILE, DO NOT EDIT --><!-- AUTO GENERATED FILE, DO NOT EDIT --><!-- AUTO GENERATED FILE, DO NOT EDIT --><!-- AUTO GENERATED FILE, DO NOT EDIT --><!-- AUTO GENERATED FILE, DO NOT EDIT --><!-- AUTO GENERATED FILE, DO NOT EDIT --><!-- AUTO GENERATED FILE, DO NOT EDIT --><!-- AUTO GENERATED FILE, DO NOT EDIT --><!-- AUTO GENERATED FILE, DO NOT EDIT --><!-- AUTO GENERATED FILE, DO NOT EDIT --><!-- AUTO GENERATED FILE, DO NOT EDIT --><!-- AUTO GENERATED FILE, DO NOT EDIT --><!-- AUTO GENERATED FILE, DO NOT EDIT --><!-- AUTO GENERATED FILE, DO NOT EDIT --><!-- AUTO GENERATED FILE, DO NOT EDIT --><!-- AUTO GENERATED FILE, DO NOT EDIT --><!-- AUTO GENERATED FILE, DO NOT EDIT --><!-- AUTO GENERATED FILE, DO NOT EDIT --><!-- AUTO GENERATED FILE, DO NOT EDIT -->' >> "$OUT"
for f in "${FILES[@]}"; do
  if [ -f "$f" ]; then
    cat "$f" >> "$OUT"
    printf "\n\n---\n\n" >> "$OUT"
  else
    echo "Warning: $f not found — run ./build.sh first" >&2
  fi
done