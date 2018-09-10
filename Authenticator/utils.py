"""
 Copyright © 2017 Bilal Elmoussaoui <bil.elmoussaoui@gmail.com>

 This file is part of Authenticator.

 Authenticator is free software: you can redistribute it and/or
 modify it under the terms of the GNU General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 Authenticator is distr  ibuted in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Authenticator. If not, see <http://www.gnu.org/licenses/>.
"""
from os import environ

from gi import require_version

require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib, Gio


def can_use_qrscanner():
    desktop = environ.get("XDG_CURRENT_DESKTOP", "").lower()
    return desktop == "gnome"


def load_pixbuf(icon_name, size):
    pixbuf = None
    theme = Gtk.IconTheme.get_default()
    if icon_name:
        try:
            icon_info = theme.lookup_icon(icon_name, size, 0)
            if icon_info:
                pixbuf = icon_info.load_icon()
        except GLib.Error:
            pass
    if not pixbuf:
        pixbuf = theme.load_icon("com.github.bilelmoussaoui.Authenticator",
                                 size, 0)

    if pixbuf and (pixbuf.props.width != size or pixbuf.props.height != size):
        pixbuf = pixbuf.scale_simple(size, size,
                                     GdkPixbuf.InterpType.BILINEAR)
    return pixbuf


def load_pixbuf_from_provider(provider_name, icon_size=48):
    if provider_name:
        provider_name = provider_name.lower().strip().replace(" ", "-")
        return load_pixbuf(provider_name, icon_size)
    else:
        return load_pixbuf(None, icon_size)
