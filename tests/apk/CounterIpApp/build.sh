#!/bin/sh

./gradlew assembleRelease && cp app/build/outputs/apk/release/app-release-unsigned.apk .
