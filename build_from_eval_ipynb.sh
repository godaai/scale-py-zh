#!/bin/bash

set -e

# remove all intermediate files
# notedown ch-ray-core/remote-class.md --run --timeout=1200 > _build/eval/ch-ray-core/remote-class.ipynb
d2lbook build rst
d2lbook build html

rm -rf docs
mkdir docs
touch docs/.nojekyll
FILE=_build/html/.nojekyll

rsync -a _build/html/* ./docs/