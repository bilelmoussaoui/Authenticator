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
from Authenticator.utils import get_icon
from gettext import gettext as _
import logging


class ApplicationRow(Gtk.ListBoxRow):

    def __init__(self, name, image):
        Gtk.ListBoxRow.__init__(self)
        self.name = name
        self.image = image
        # Create the list row
        self.create_row()

    def get_name(self):
        """
            Get the application label
            :return: (str): application label
        """
        return self.name

    def get_icon_name(self):
        return self.image

    def create_row(self):
        """
            Create ListBoxRow
        """
        self.get_style_context().add_class("application-list-row")
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        # Application logo
        application_logo = get_icon(self.image, 48)
        application_image = Gtk.Image(xalign=0)
        application_image.set_from_pixbuf(application_logo)
        hbox.pack_start(application_image, False, True, 6)

        # Application name
        application_name = Gtk.Label(xalign=0)
        application_name.get_style_context().add_class("application-name")
        application_name.set_text(self.name)
        hbox.pack_start(application_name, True, True, 6)

        vbox.pack_start(hbox, True, True, 6)
        self.add(vbox)
