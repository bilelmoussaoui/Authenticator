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
from gi.repository import Gtk, Gdk
import logging
from hashlib import sha256
from gettext import gettext as _
from Authenticator.const import settings
from Authenticator.models.observer import Observer


class LoginWindow(Gtk.Box, Observer):

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
            self.toggle_lock()
            password_entry.set_text("")
        else:
            password_entry.set_icon_from_icon_name(
                Gtk.EntryIconPosition.SECONDARY, "dialog-error-symbolic")

    def __on_key_press(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval).lower()
        if self.window.is_locked():
            if keyname == "return":
                self.on_unlock()
                return True
        else:
            pass_enabled = settings.get_can_be_locked()
            if keyname == "l" and pass_enabled:
                if event.state & Gdk.ModifierType.CONTROL_MASK:
                    self.toggle_lock()
                    return True

        return False

    def toggle_lock(self, *args):
        """
            Lock/unlock the application
        """
        pass_enabled = settings.get_can_be_locked()
        if pass_enabled:
            settings.set_is_locked(not settings.get_is_locked())
            self.window.counter = 0
            if settings.get_is_locked():
                self.self.password_entry.grab_focus_without_selecting()
                self.window.emit("locked", True)
            else:
                self.window.emit("unlocked", True)

    def update(self, *args, **kwargs):
        is_locked = kwargs.pop("locked", None)
        is_unlocked = kwargs.pop("unlocked", None)
        if is_locked:
            self.set_visible(True)
            self.set_no_show_all(False)
            settings.set_is_locked(True)
        elif is_unlocked:
            settings.set_is_locked(False)
            self.set_visible(False)
            self.set_no_show_all(True)
