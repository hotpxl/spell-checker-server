#!/bin/bash
set -euo pipefail

file_path="$(readlink -f "$(dirname "${BASH_SOURCE[0]}")")"
pushd "${file_path}" > /dev/null

mkdir -p ./server/bin
curl --fail --location --remote-header-name --remote-name "https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2"
tar xzf phantomjs-2.1.1-linux-x86_64.tar.bz2
cp ./phantomjs-2.1.1-linux-x86_64/bin/phantomjs ./server/bin/
