#!/bin/bash
set -e

BRANCH="$(git branch --show-current)"
COMMIT="$(git rev-parse --short HEAD)"
PWD="$(pwd)"

echo "Check changes for ${BRANCH} on commit ${COMMIT} in ${PWD}"
if [ $(git status --porcelain | wc -l) -eq "0" ]; then
  echo "  🟢 Git repo is clean."
else
  echo "  🔴 Git repo has changes. Commit"
  git add data
  git commit -m "Commit to ${BRANCH} changes for because of changes in ${COMMIT}"
  git push origin ${BRANCH}
fi
