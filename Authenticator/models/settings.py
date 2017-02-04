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
import logging
from gi.repository import Gio, GLib
from hashlib import sha256


class Settings(Gio.Settings):

    def __init__(self):
        Gio.Settings.__init__(self)

    def new():
        gsettings = Gio.Settings.new("org.gnome.Authenticator")
        gsettings.__class__ = Settings
        return gsettings

    def get_window_size(self):
        return tuple(self.get_value('window-size'))

    def set_window_size(self, size):
        size = GLib.Variant('ai', list(size))
        self.set_value('window-size', size)

    def get_default_size(self):
        return tuple(self.get_default_value('window-size'))

    def get_window_position(self):
        return tuple(self.get_value('window-position'))

    def set_window_postion(self, position):
        position = GLib.Variant('ai', list(position))
        self.set_value('window-position', position)

    def set_is_night_mode(self, statue):
        self.set_boolean('night-mode', statue)

    def get_is_night_mode(self):
        return self.get_boolean('night-mode')

    def set_can_be_locked(self, status):
        self.set_boolean('state', status)

    def get_can_be_locked(self):
        return self.get_boolean('state')

    def set_is_locked(self, statue):
        self.set_boolean('locked', statue)

    def get_is_locked(self):
        return self.get_boolean('locked')

    def set_password(self, password):
        password = sha256(password.encode('utf-8')).hexdigest()
        self.set_string("password", password)

    def compare_password(self, password):
        password = sha256(password.encode('utf-8')).hexdigest()
        return password == self.get_password()

    def is_password_set(self):
        return len(self.get_password()) != 0

    def get_password(self):
        return self.get_string("password")

    def get_auto_lock_status(self):
        return self.get_boolean("auto-lock")

    def set_auto_lock_status(self, status):
        self.set_boolean("auto-lock", status)

    def get_auto_lock_time(self):
        return self.get_int("auto-lock-time")

    def set_auto_lock_time(self, auto_lock_time):
        if auto_lock_time < 1 or auto_lock_time > 15:
            auto_lock_time = 3
        self.set_int("auto-lock-time", auto_lock_time)
