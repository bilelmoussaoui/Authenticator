#!/usr/bin/env sh

find . -name "*.py" -exec autopep8 --in-place {} \;
