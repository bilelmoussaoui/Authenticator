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
from gi.repository import Gtk, GLib, Gio, Gdk
import logging


class ConfirmationMessage(Gtk.Window):
    result = None

    def __init__(self, parent, message):
        try:
            self.dialog = Gtk.MessageDialog(
                transient_for=parent,
                modal=True,
                destroy_with_parent=True,
                text=message,
                buttons=Gtk.ButtonsType.OK_CANCEL)
            logging.debug("Confirmation message created successfully")
        except Exception as e:
            logging.error(str(e))

    def show(self):
        """
            Show confirmation dialog
        """
        try:
            self.result = self.dialog.run()
            self.dialog.hide()
        except AttributeError:
            logging.error("Confiramation message was not created correctly")
            return None

    def get_confirmation(self):
        """
            get confirmation
        """
        return self.result == Gtk.ResponseType.OK

    def destroy(self):
        """
            Destroy the message
        """
        self.dialog.destroy()
