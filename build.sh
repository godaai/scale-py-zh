#!/bin/bash

set -e

jupyter-book build ./

rm -rf docs
mkdir docs
touch docs/.nojekyll
cp -r datasets ./docs/
rsync -a _build/html/* ./docs/