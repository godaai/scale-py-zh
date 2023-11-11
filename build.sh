#!/bin/bash

set -e

jupyter-book build ./

rm -rf docs
mkdir docs
touch docs/.nojekyll
touch docs/CNAME
echo "edaai.org" >> docs/CNAME
cp -r datasets ./docs/
rsync -a _build/html/* ./docs/