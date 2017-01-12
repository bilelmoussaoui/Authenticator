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
from Authenticator.models.observer import Observer

class LoginWindow(Gtk.Box, Observer):
    password_entry = None
    unlock_button = None

    def __init__(self, application, window):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        self.app = application
        self.window = window
        self.password_entry = Gtk.Entry()
        self.unlock_button = Gtk.Button()
        self.generate()
        self.window.connect("key-press-event", self.__on_key_press)

    def generate(self):
        password_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.password_entry.set_visibility(False)
        self.password_entry.set_placeholder_text(_("Enter your password"))
        password_box.pack_start(self.password_entry, False, False, 6)

        self.unlock_button.set_label(_("Unlock"))
        self.unlock_button.connect("clicked", self.on_unlock)

        password_box.pack_start(self.unlock_button, False, False, 6)
        self.pack_start(password_box, True, False, 6)

    def on_unlock(self, *args):
        """
            Password check and unlock
        """
        typed_pass = self.password_entry.get_text()
        ecrypted_pass = sha256(typed_pass.encode("utf-8")).hexdigest()
        login_pass = self.app.cfg.read("password", "login")
        if ecrypted_pass == login_pass or login_pass == typed_pass == "":
            self.password_entry.set_icon_from_icon_name(
                Gtk.EntryIconPosition.SECONDARY, None)
            self.toggle_lock()
            self.password_entry.set_text("")
        else:
            self.password_entry.set_icon_from_icon_name(
                Gtk.EntryIconPosition.SECONDARY, "dialog-error-symbolic")

    def __on_key_press(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval).lower()
        if self.window.is_locked():
            if keyname == "return":
                self.on_unlock()
                return True
        else:
            pass_enabled = self.app.cfg.read("state", "login")
            if keyname == "l" and pass_enabled:
                if event.state & Gdk.ModifierType.CONTROL_MASK:
                    self.toggle_lock()
                    return True

        return False

    def toggle_lock(self, *args):
        """
            Lock/unlock the application
        """
        pass_enabled = self.app.cfg.read("state", "login")
        if pass_enabled:
            self.app.locked = not self.app.locked
            self.window.counter = 0
            if self.app.locked:
                self.focus()
                self.window.emit("locked", True)
            else:
                self.window.emit("unlocked", True)

    def update(self, *args, **kwargs):
        is_locked = kwargs.pop("locked", None)
        is_unlocked = kwargs.pop("unlocked", None)
        if is_locked:
            self.show()
        elif is_unlocked:
            self.hide()

    def toggle(self, visible):
        self.set_visible(visible)
        self.set_no_show_all(not visible)

    def hide(self):
        self.toggle(False)

    def show(self):
        self.toggle(True)

    def focus(self):
        self.password_entry.grab_focus_without_selecting()
