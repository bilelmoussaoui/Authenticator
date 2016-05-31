#!/bin/sh

mkdir -p m4

echo "Creating m4/aclocal.m4 ..."
test -r m4/aclocal.m4 || touch m4/aclocal.m4

echo "Running glib-gettextize... Ignore non-fatal messages."
echo "no" | glib-gettextize --force --copy

echo "Making m4/aclocal.m4 writable ..."
test -r m4/aclocal.m4 && chmod u+w m4/aclocal.m4

echo "Running intltoolize..."
intltoolize --force --copy --automake || return 1

echo "Running aclocal..."
aclocal || return 1

echo "Running libtoolize..."
libtoolize || return 1

echo "Running autoheader..."
autoheader || return 1

echo "Running autoconf..."
autoconf || return 1

echo "Running automake..."
automake --add-missing || return 1

echo "Running configure..."
./configure "$@" || return 1
