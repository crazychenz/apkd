#!/usr/bin/env bash

#npx create-docusaurus@latest docusaurus classic
#npx docusaurus telemetry disable
#npm config set update-notifier false
#npx update-browserslist-db@latest

export PROJ_PATH=$(realpath $(dirname $0)/../../..)

OUT_PATH=$PROJ_PATH/outputs/docs/docusaurus
mkdir -p $OUT_PATH

pushd $PROJ_PATH/docs/builders/docusaurus

npm_config_update_notifier=false \
DOCUSAURUS_DISABLE_TELEMETRY=1 \
BROWSERSLIST_UPDATE_DB=false \
npm run build -- --out-dir $OUT_PATH
rsync -a \
  --include='*/' \
  --include='*.jpg' \
  --include='*.png' \
  --include='*.svg' \
  --exclude='*' \
  $PROJ_PATH/docs/builders/docusaurus/docs/ $OUT_PATH/docs/

popd