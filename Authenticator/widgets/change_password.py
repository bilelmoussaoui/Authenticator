"""
 Copyright © 2017 Bilal Elmoussaoui <bil.elmoussaoui@gmail.com>

 This file is part of Gnome Authenticator.

 Gnome Authenticator is free software: you can redistribute it and/or
 modify it under the terms of the GNU General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 TwoFactorAuth is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Gnome Authenticator. If not, see <http://www.gnu.org/licenses/>.
"""
from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from ..models import Settings
from gettext import gettext as _
from hashlib import sha256
import logging


class PasswordWindow:

    def __init__(self, parent):
        self.builder = Gtk.Builder.new_from_resource(
            "/org/gnome/Authenticator/change_password.ui")
        self.builder.connect_signals({
            "on_quit": self.close_window,
            "on_type": self.__on_type_password,
            "on_apply": self.__update_password
        })
        self.window = self.builder.get_object("ChangePasswordWindow")
        self.window.set_transient_for(parent)
        self.old_entry = self.builder.get_object("OldPasswordEntry")
        self.new_entry = self.builder.get_object("NewPasswordEntry")
        self.apply_button = self.builder.get_object("ApplyButton")
        self.repeat_entry = self.builder.get_object("RepeatPasswordEntry")
        if not Settings.get_default().password:
            self.builder.get_object("PasswordGrid").remove_row(0)
        self.window.connect("key_press_event", self.on_key_press)

    def show_window(self):
        self.window.show_all()

    def on_key_press(self, key, key_event):
        """
            Keyboard listener handler
        """
        if Gdk.keyval_name(key_event.keyval) == "Escape":
            self.close_window()

    def __update_password(self, *args):
        """
            Update user password
        """
        settings.set_password(self.new_entry.get_text())
        logging.debug("Password changed successfully")
        self.close_window()

    def __on_type_password(self, entry):
        """
            Validate the old & new password
        """
        # Check the new typed password
        if (self.new_entry.get_text() != self.repeat_entry.get_text()
            or len(self.new_entry.get_text()) == 0
                or len(self.repeat_entry.get_text()) == 0):
            are_diff = True
        else:
            are_diff = False
        # Check if the old password is set
        if settings.is_password_set():
            if not settings.compare_password(self.old_entry.get_text()):
                old_is_valid = False
            else:
                old_is_valid = True
            self.__set_entry_status_icon(self.old_entry, old_is_valid)
        else:
            old_is_valid = True

        self.__set_entry_status_icon(self.new_entry, not are_diff)
        self.__set_entry_status_icon(self.repeat_entry, not are_diff)
        self.apply_button.set_sensitive(not are_diff and old_is_valid)

    def __set_entry_status_icon(self, entry, is_valid=False):
        # Private function to change the Gtk.Entry secondary icon
        if is_valid:
            icon = None
        else:
            icon = "dialog-error-symbolic"
        entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, icon)

    def close_window(self, *args):
        """
            Close the window
        """
        logging.debug("Closing PasswordWindow")
        self.window.destroy()
