#!/usr/bin/env bash

TAG=$1

./scripts/build-pkgs.sh ${TAG}.$(git describe --tags | sed 's/-\([0-9]*\)-g\(.*\)/!dev\1+g\2/' | cut -d '!' -f2)