#!/bin/bash
set -ex
# openssl aes-256-cbc -v -k "${travis_key_password}" -d -md sha256 -a -in .travis_key.enc -out travis_key
chmod 400 travis_key
echo "Host github.com" > ~/.ssh/config
echo "  IdentityFile $(pwd)/travis_key" >> ~/.ssh/config
git remote set-url origin git@github.com:AaronDMarasco/rpm-cookbook.git
ssh-keyscan -H github.com >> ~/.ssh/known_hosts
if ! git diff --exit-code README.md; then
  git checkout ${TRAVIS_BRANCH}
  git add README.md
  git commit --message "Travis build ${TRAVIS_BUILD_NUMBER} of README.md: <${TRAVIS_BUILD_WEB_URL}> [ci skip]"
  git push -v
fi
