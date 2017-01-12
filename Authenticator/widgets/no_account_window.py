# -*- coding: utf-8 -*-
"""
 Copyright © 2016 Bilal Elmoussaoui <bil.elmoussaoui@gmail.com>

 This file is part of Gnome-TwoFactorAuth.

 Gnome-TwoFactorAuth is free software: you can redistribute it and/or
 modify it under the terms of the GNU General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 TwoFactorAuth is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Gnome-TwoFactorAuth. If not, see <http://www.gnu.org/licenses/>.
"""
from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk
import logging
from gettext import gettext as _
from Authenticator.models.observer import Observer

class NoAccountWindow(Gtk.Box, Observer):

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL,
                         spacing=6)
        self.generate()

    def generate(self):
        logo_image = Gtk.Image()
        logo_image.set_from_icon_name("dialog-information-symbolic",
                                      Gtk.IconSize.DIALOG)
        no_apps_label = Gtk.Label()
        no_apps_label.set_text(_("There's no account at the moment"))

        self.pack_start(logo_image, False, False, 6)
        self.pack_start(no_apps_label, False, False, 6)

    def update(self, *args, **kwargs):
        unlocked = kwargs.pop("unlocked", None)
        locked = kwargs.pop("locked", None)
        counter = kwargs.pop("counter", None)
        if counter != 0 or locked:
            self.hide()
        elif unlocked or counter == 0:
            self.show()

    def toggle(self, visible):
        self.set_visible(visible)
        self.set_no_show_all(not visible)

    def is_visible(self):
        return self.get_visible()

    def hide(self):
        self.toggle(False)

    def show(self):
        self.toggle(True)
