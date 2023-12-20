#!/bin/bash

set -e

sphinx-build -b html ./ ./_build/html

rm -rf docs
mkdir docs
touch docs/.nojekyll
cp -r datasets ./docs/
rsync -a _build/html/* ./docs/