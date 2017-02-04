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
from gi.repository import Gtk, Gdk, Gio
import logging
from hashlib import sha256
from gettext import gettext as _
from Authenticator.const import settings

class LoginWindow(Gtk.Box):

    def __init__(self, window):
        self.window = window
        self.generate()
        self.window.connect("key-press-event", self.__on_key_press)

    def generate(self):
        Gtk.Box.__init__(self)
        self.builder = Gtk.Builder()
        self.builder.connect_signals({
            "on_unlock" : self.on_unlock
        })
        self.builder.add_from_resource('/org/gnome/Authenticator/login.ui')
        login_window = self.builder.get_object("loginWindow")
        settings.bind("locked", login_window, "no_show_all", Gio.SettingsBindFlags.INVERT_BOOLEAN)
        settings.bind("locked", login_window, "visible", Gio.SettingsBindFlags.GET)
        self.pack_start(login_window, True, False, 0)

    def on_unlock(self, *args):
        """
            Password check and unlock
        """
        password_entry = self.builder.get_object("passwordEntry")
        typed_pass = password_entry.get_text()
        ecrypted_pass = sha256(typed_pass.encode("utf-8")).hexdigest()
        if (settings.compare_password(typed_pass)
            or settings.get_password() == typed_pass == ""):
            password_entry.set_icon_from_icon_name(
                Gtk.EntryIconPosition.SECONDARY, None)
            settings.set_is_locked(False)
            password_entry.set_text("")
        else:
            password_entry.set_icon_from_icon_name(
                Gtk.EntryIconPosition.SECONDARY, "dialog-error-symbolic")

    def __on_key_press(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval).lower()
        if settings.get_is_locked():
            if keyname == "return":
                self.on_unlock()
                return True
        else:
            pass_enabled = settings.get_can_be_locked()
            if keyname == "l" and pass_enabled:
                if event.state & Gdk.ModifierType.CONTROL_MASK:
                    self.on_lock()
                    return True

        return False

    def on_lock(self, *args):
        """
            Lock/unlock the application
        """
        pass_enabled = settings.get_can_be_locked()
        if pass_enabled:
            settings.set_is_locked(True)
            self.window.counter = 0
            password_entry = self.builder.get_object("passwordEntry")
            password_entry.grab_focus_without_selecting()
            settings.set_is_locked(True)
