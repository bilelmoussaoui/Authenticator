#!/usr/bin/env sh
rm -rf builddir
meson builddir --prefix=/usr
sudo ninja -C builddir install

