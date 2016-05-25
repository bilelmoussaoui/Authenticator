#!/bin/sh

autoreconf --install || exit 1
echo "Running configure script with no arguments"
./configure
