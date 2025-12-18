#!/usr/bin/env bash
# Helper to initialize git repo, make first commit and push to a remote

set -euo pipefail

if [ -z "${1-}" ]; then
  echo "Usage: $0 <git-remote-url> [branch]"
  echo "Example: $0 git@github.com:youruser/yourrepo.git main"
  exit 1
fi

REMOTE_URL=$1
BRANCH=${2-main}

git init
git add .
git commit -m "chore: initial project import"
git branch -M "$BRANCH"
git remote add origin "$REMOTE_URL"
git push -u origin "$BRANCH"

echo "Pushed to $REMOTE_URL ($BRANCH)"
