#!/bin/bash

set -e

jupyter-book build ./

rm -rf docs
mkdir docs
touch docs/.nojekyll

rsync -a _build/html/* ./docs/