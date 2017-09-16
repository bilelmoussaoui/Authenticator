#!/usr/bin/env python3

from os import environ, path
from subprocess import call

PREFIX = environ.get('MESON_INSTALL_PREFIX', '/usr/local')
DATA_DIR = path.join(PREFIX, 'share')

if not destdir:
    print('Updating icon cache...')
    call(['gtk-update-icon-cache', '-qtf', path.join(DATA_DIR, 'icons', 'hicolor')])
    print("compiling new schemas")
    call(["glib-compile-schemas", path.join(DATA_DIR, 'share/glib-2.0/schemas/')])
