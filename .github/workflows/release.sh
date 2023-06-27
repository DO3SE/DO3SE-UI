#!/bin/bash
set -e

[ -z "$1" ] && echo "make sure to input [patch|minor|major]" && exit 1;
source venv/bin/activate
if [ -z "$(git status --porcelain)" ]; then
  echo "Working directory clean"
else
    git stash save -u "hold_build_deploy"
fi

pip freeze -r requirements/freeze.txt > requirements/freeze.txt
pip list | awk '{ printf "%-40s %-40s\n", $1, $2}' > requirements/list.txt

if [ -z "$(git status --porcelain)" ]; then
  echo "Working directory clean"
else
  git add requirements/freeze.txt
  git add requirements/list.txt
  git commit -m "update dependencies lists"
fi

bumpversion $1
RELEASE_BRANCH=${2:-RELEASE}
echo $RELEASE_BRANCH

git branch -D $RELEASE_BRANCH && \
git checkout --orphan $RELEASE_BRANCH && \
git commit -m $RELEASE_BRANCH && \
git push --force --set-upstream origin $RELEASE_BRANCH && \
git push --tags
git checkout master

if [ -z "$(git status --porcelain)" ]; then
  echo "Working directory clean"
else
    git stash pop
fi