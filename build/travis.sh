#!/bin/bash
set -e
echo "Host github.com" > ~/.ssh/config
echo "  IdentityFile $(pwd)/travis_key" >> ~/.ssh/config
chmod 400 travis_key
set -x
git remote set-url origin git@github.com:AaronDMarasco/rpm-cookbook.git
ssh-keyscan -H github.com >> ~/.ssh/known_hosts
if ! git diff --exit-code README.md; then
  git checkout ${TRAVIS_BRANCH}
  git add README.md
  git commit --message "Travis build ${TRAVIS_BUILD_NUMBER} of README.md: <${TRAVIS_BUILD_WEB_URL}> [ci skip]"
  git push -v
fi
