#!/usr/bin/env bash

# Note: Set env var TYPST to location of typst binary.
#   Example: TYPST=./typst ./do builddocs

set -e

export PROJ_PATH=$(realpath $(dirname $0)/../../..)
DOCS_PATH=$PROJ_PATH/docs/manual
TMPL_PATH=$PROJ_PATH/docs/builders/pandoc
OUT_PATH=$PROJ_PATH/outputs/docs/pandoc
RESOURCE_PATH="$(find "${DOCS_PATH}" -type d | paste -sd: -)"
TARGET="${1:-all}"
TYPST=${TYPST:-typst}

MANUAL_FILES=(
  "${DOCS_PATH}/1-where-to-start/index.md"
  "${DOCS_PATH}/2-introduction/index.md"
  "${DOCS_PATH}/2-introduction/2.1-overview.md"
  "${DOCS_PATH}/2-introduction/2.2-install.md"

  "${DOCS_PATH}/3-end-user/index.md"
  "${DOCS_PATH}/3-end-user/3.1-overview.md"
  "${DOCS_PATH}/3-end-user/3.2-primers.md"
  
  "${DOCS_PATH}/4-integration/index.md"
  "${DOCS_PATH}/4-integration/4.2-quick-start.md"

  "${DOCS_PATH}/5-use-cases/index.md"

  "${DOCS_PATH}/6-api-reference/index.md"

  "${DOCS_PATH}/7-maintainer/index.md"
  "${DOCS_PATH}/7-maintainer/7.2-architecture.md"
  "${DOCS_PATH}/7-maintainer/7.3-dev-environment.md"
  "${DOCS_PATH}/7-maintainer/7.4-code-base.md"
  "${DOCS_PATH}/7-maintainer/7.5-testing/index.md"
  "${DOCS_PATH}/7-maintainer/7.5-testing/7.5.1-overview.md"
  "${DOCS_PATH}/7-maintainer/7.6-release.md"
  "${DOCS_PATH}/7-maintainer/7.7-roadmap.md"
  "${DOCS_PATH}/7-maintainer/7.8-commentary/index.md"

  "${DOCS_PATH}/8-tutorials/index.md"

  "${TMPL_PATH}/metadata-tail.yaml"
)


# TODO: Consider putting side effect in create_folders procedure.
mkdir -p $OUT_PATH
# TODO: Is this copy needed?
cp ${DOCS_PATH}/assets/manual.css $OUT_PATH/


FILTERS=(
  "$TMPL_PATH/toc-control.lua"
  "$TMPL_PATH/crosslink.lua"
  "$TMPL_PATH/rules.lua"
  "$TMPL_PATH/num-headings-md.lua"
)
filter_args() {
  local args=()
  for f in "${FILTERS[@]}"; do args+=(--lua-filter "$f"); done
  printf '%s\n' "${args[@]}"
}


# UNUSED
update_usecases() {
  log "Pre-processing: refreshing generated sections"
  python3 "$ROOT_DIR/scripts/update_use_cases.py" \
    "$DOCS_DIR/guides/advanced-usage.md" \
    --debug-json "$DEBUG_DIR/use-case-refresh.json"
}


build_json() {
  echo "---- Building JSON"
  pandoc "${MANUAL_FILES[@]}" \
    --metadata-file="${DOCS_PATH}/_meta/book.yaml" \
    --toc --toc-depth=3 --number-sections \
    --resource-path="$RESOURCE_PATH" \
    --extract-media=media \
    $(filter_args) \
    -f markdown -t json \
    -o $OUT_PATH/api-doc-reference.json
}


build_typ() {
  echo "---- Building TYP"
  (
    cd $OUT_PATH
    trace="$OUT_PATH/yannt-manual-pandoc-typ-trace.json" \
    pandoc "${MANUAL_FILES[@]}" \
      --metadata-file="${DOCS_PATH}/_meta/book.yaml" \
      -f markdown -t typst \
      --template "$TMPL_PATH/manual.typst" \
      --toc --toc-depth=3 --number-sections \
      -M crosslink_mode=internal \
      --resource-path="$RESOURCE_PATH" \
      --extract-media=media \
      $(filter_args) \
      --trace \
      -o "$OUT_PATH/yannt-manual.typ" \
      2>&1 | tee "$OUT_PATH/yannt-manual-pandoc-typ-stderr.log" 2>&1 >/dev/null
  )
}


build_pdf() {
  echo "---- Building PDF"

  if command -v $TYPST >/dev/null 2>&1; then
    $TYPST compile \
      --font-path "$TMPL_PATH" \
      "$OUT_PATH/yannt-manual.typ" "$OUT_PATH/yannt-manual.pdf" \
      2>"$OUT_PATH/pdf-typst-stderr.log"
  else
    echo "WARNING: 'typst' binary not found on PATH; skipping typst compile step."
    echo "  Install from https://github.com/typst/typst and re-run."
  fi
}


build_single_html() {
  echo "---- Building Single HTML"
  cp ${DOCS_PATH}/assets/manual.css $OUT_PATH/
  (
    cd $OUT_PATH
    trace="$OUT_PATH/yannt-manual-pandoc-html-single-trace.json" \
    pandoc "${MANUAL_FILES[@]}" \
      --metadata-file="${DOCS_PATH}/_meta/book.yaml" \
      -f markdown -t html5 \
      -s --toc --toc-depth=3 --number-sections \
      -M crosslink_mode=internal \
      --resource-path="$RESOURCE_PATH" \
      --extract-media=media \
      --css=manual.css \
      $(filter_args) \
      --trace \
      -o $OUT_PATH/yannt-manual-single.html \
      2>&1 | tee "$OUT_PATH/yannt-manual-pandoc-single-html-stderr.log" 2>&1 >/dev/null
  )
}


build_multi_html() {
  echo "---- Building Multiple HTML"
  local out_dir="$OUT_PATH/html"
  local stderr_log=$OUT_PATH/yannt-manual-pandoc-multi-html-stderr.log

  rm -rf "$out_dir"

  pandoc "${MANUAL_FILES[@]}" \
    --metadata-file="${DOCS_PATH}/_meta/book.yaml" \
    -f markdown -t chunkedhtml \
    --toc --toc-depth=3 --number-sections \
    -M crosslink_mode=html-multipage \
    --resource-path="$RESOURCE_PATH" \
    --extract-media=media \
    --css="assets/manual.css" \
    $(filter_args) \
    -o "$out_dir" \
    2>&1 | tee "$stderr_log"

  mkdir -p "$out_dir/assets"
  cp -r "${DOCS_PATH}/assets/." "$out_dir/assets/"
}


build_gfm() {
  echo "---- Building Multiple GFM Markdown"
  local out_dir="$OUT_PATH/gfm"
  local stderr_log=$OUT_PATH/yannt-manual-pandoc-multi-gfm-stderr.log

  rm -rf "$out_dir"
  mkdir -p $out_dir/assets
  cp -r "${DOCS_PATH}/assets/." "$out_dir/assets/"

  echo "" > $stderr_log

  local position=5
  for src in "${MANUAL_FILES[@]}"; do
    local rel="${src#"${DOCS_PATH}"/}"
    local out="$out_dir/$rel"
    mkdir -p "$(dirname "$out")"

    pandoc "$src" \
      -f markdown -t gfm \
      --standalone --number-sections \
      -M crosslink_mode=commonmark \
      -M sidebar_position="$position" \
      $(filter_args) \
      -o "$out" \
      2>&1 | tee -a $stderr_log 2>&1 >/dev/null
    position=$((position + 5))
  done

  rsync -a \
    --include='*/' \
    --include='*.jpg' \
    --include='*.png' \
    --include='*.svg' \
    --exclude='*' \
    "${DOCS_PATH}/" "${out_dir}/"

  # _category_.json controls a folder's label/position/collapsed-state in
  # Docusaurus's autogenerated sidebar. These are authored once, alongside
  # the content they describe, and just need to land in the same relative
  # spot in the output tree -- copy them over unmodified, same as assets/.
  while IFS= read -r -d '' cat_file; do
    local rel="${cat_file#"${DOCS_PATH}"/}"
    local out="$out_dir/$rel"
    mkdir -p "$(dirname "$out")"
    cp "$cat_file" "$out"
  done < <(find "${DOCS_PATH}" -name "_category_.json" -print0)
}


build_commonmark_x() {
  echo "---- Building Multiple (Extended) CommonMark"
  local out_dir="$OUT_PATH/commonmark_x"
  local stderr_log=$OUT_PATH/yannt-manual-pandoc-multi-commonmark_x-stderr.log

  rm -rf "$out_dir"
  mkdir -p $out_dir/assets
  cp -r "${DOCS_PATH}/assets/." "$out_dir/assets/"

  echo "" > $stderr_log

  local position=5
  for src in "${MANUAL_FILES[@]}"; do
    local rel="${src#"${DOCS_PATH}"/}"
    local out="$out_dir/$rel"
    mkdir -p "$(dirname "$out")"

    pandoc "$src" \
      -f markdown -t commonmark_x \
      --standalone --number-sections \
      -M crosslink_mode=commonmark \
      -M sidebar_position="$position" \
      $(filter_args) \
      -o "$out" \
      2>&1 | tee -a $stderr_log 2>&1 >/dev/null
    position=$((position + 5))
  done

  # _category_.json controls a folder's label/position/collapsed-state in
  # Docusaurus's autogenerated sidebar. These are authored once, alongside
  # the content they describe, and just need to land in the same relative
  # spot in the output tree -- copy them over unmodified, same as assets/.
  while IFS= read -r -d '' cat_file; do
    local rel="${cat_file#"${DOCS_PATH}"/}"
    local out="$out_dir/$rel"
    mkdir -p "$(dirname "$out")"
    cp "$cat_file" "$out"
  done < <(find "${DOCS_PATH}" -name "_category_.json" -print0)
}


build_commonmark() {
  echo "---- Building Multiple CommonMark"
  local out_dir="$OUT_PATH/commonmark"
  local stderr_log=$OUT_PATH/yannt-manual-pandoc-multi-commonmark-stderr.log

  rm -rf "$out_dir"
  mkdir -p $out_dir/assets
  cp -r "${DOCS_PATH}/assets/." "$out_dir/assets/"

  echo "" > $stderr_log

  local position=5
  for src in "${MANUAL_FILES[@]}"; do
    local rel="${src#"${DOCS_PATH}"/}"
    local out="$out_dir/$rel"
    mkdir -p "$(dirname "$out")"

    pandoc "$src" \
      -f markdown -t commonmark+raw_html \
      --standalone --number-sections \
      -M crosslink_mode=commonmark \
      -M sidebar_position="$position" \
      $(filter_args) \
      -o "$out" \
      2>&1 | tee -a $stderr_log 2>&1 >/dev/null
    position=$((position + 5))
  done

  # _category_.json controls a folder's label/position/collapsed-state in
  # Docusaurus's autogenerated sidebar. These are authored once, alongside
  # the content they describe, and just need to land in the same relative
  # spot in the output tree -- copy them over unmodified, same as assets/.
  while IFS= read -r -d '' cat_file; do
    local rel="${cat_file#"${DOCS_PATH}"/}"
    local out="$out_dir/$rel"
    mkdir -p "$(dirname "$out")"
    cp "$cat_file" "$out"
  done < <(find "${DOCS_PATH}" -name "_category_.json" -print0)
}


build_epub() {
  echo "---- Building EPUB"
  pandoc $TMPL_PATH/metadata.yaml $CHAPTERS $TMPL_PATH/metadata-tail.yaml \
    --lua-filter=$TMPL_PATH/api-doc-filter.lua \
    --from markdown+raw_html+simple_tables \
    --toc --number-sections \
    -o $OUT_PATH/api-doc-reference.epub
}

case "$TARGET" in
  pdf)
    # preprocess
    build_json
    build_typ
    build_pdf
    ;;
  html)
    # preprocess
    build_single_html
    build_multi_html
    ;;
  commonmark)
    # preprocess
    build_commonmark
    build_commonmark_x
    build_gfm
    ;;
  all)
    # preprocess
    build_json
    build_typ
    build_pdf
    build_single_html
    build_multi_html
    build_commonmark
    build_commonmark_x
    build_gfm
    ;;
  *)
    echo "usage: $0 [pdf|html|commonmark|all]" >&2
    exit 2
    ;;
esac


exit 0

