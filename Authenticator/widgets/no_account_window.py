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
from gi.repository import Gtk, Gio
import logging
from gettext import gettext as _
from Authenticator.const import settings

class NoAccountWindow(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL,
                         spacing=6)        
        # hidden by default
        self.set_visible(False)
        self.set_no_show_all(True)

        self.generate()

    def generate(self):
        logo_image = Gtk.Image()
        logo_image.set_from_icon_name("dialog-information-symbolic",
                                      Gtk.IconSize.DIALOG)
        no_apps_label = Gtk.Label()
        no_apps_label.set_text(_("There's no account at the moment"))

        self.pack_start(logo_image, False, False, 6)
        self.pack_start(no_apps_label, False, False, 6)