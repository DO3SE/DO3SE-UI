#!/bin/bash
# get version number from file using cat
APP_VERSION=$(cat src/version)
TAG="v$APP_VERSION"
gh release create $TAG dist/do3se-$APP_VERSION-*.whl -R https://github.com/SEI-DO3SE/do3se_releases_private --notes "Release $TAG"

