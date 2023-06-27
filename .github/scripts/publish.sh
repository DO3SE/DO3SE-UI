#!/bin/bash
# get version number from file using cat
APP_VERSION=$(cat src/version)
TAG="v$APP_VERSION"
gh release create $TAG DO3SE-UI.zip -R https://github.com/SEI-DO3SE/do3se_releases_private
