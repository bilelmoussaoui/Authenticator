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
    """Settings handler."""
    # Default Settings instance
    instance = None

    def __init__(self):
        Gio.Settings.__init__(self)

    def new():
        gsettings = Gio.Settings.new("org.gnome.Authenticator")
        gsettings.__class__ = Settings
        return gsettings

    @staticmethod
    def get_default():
        """Return the default instance of Settings."""
        if Settings.instance is None:
            Settings.instance = Settings.new()
        return Settings.instance

    @property
    def window_size(self):
        """Return the window size."""
        return tuple(self.get_value('window-size'))

    @window_size.setter
    def window_size(self, size):
        """Set the window size."""
        size = GLib.Variant('ai', list(size))
        self.set_value('window-size', size)

    @property
    def default_size(self):
        """Return the default window size."""
        return tuple(self.get_default_value('window-size'))

    @property
    def window_position(self):
        """Return the window's position."""
        return tuple(self.get_value('window-position'))

    @window_position.setter
    def window_postion(self, position):
        """Set the window postion."""
        position = GLib.Variant('ai', list(position))
        self.set_value('window-position', position)

    @is_night_mode.setter
    def is_night_mode(self, status):
        """Set the night mode."""
        self.set_boolean('night-mode', status)

    @property
    def is_night_mode(self):
        """Is night mode?"""
        return self.get_boolean('night-mode')

    @can_be_locked.setter
    def can_be_locked(self, status):
        """set the app to be locked."""
        self.set_boolean('state', status)

    @property
    def can_be_locked(self):
        """Return if the app can be locked or not."""
        return self.get_boolean('state')

    @is_locked.status
    def is_locked(self, status):
        """Set the app to be locked."""
        self.set_boolean('locked', status)

    @property
    def is_locked(self):
        """Return if the app is locked."""
        return self.get_boolean('locked')

    @password.setter
    def password(self, password):
        """Set a new password."""
        password = sha256(password.encode('utf-8')).hexdigest()
        self.set_string("password", password)

    def compare_password(self, password):
        """Compare a password with the current one."""
        password = sha256(password.encode('utf-8')).hexdigest()
        return password == self.password

    @property
    def password(self):
        """Return the password."""
        return self.get_string("password")

    @property
    def auto_lock(self):
        """Return the Auto lock status."""
        return self.get_boolean("auto-lock")

    @auto_lock.setter
    def auto_lock(self, status):
        """Set the auto lock status."""
        self.set_boolean("auto-lock", status)

    @property
    def auto_lock_time(self):
        """Get auto lock time."""
        return self.get_int("auto-lock-time")

    @auto_lock_time.setter
    def auto_lock_time(self, auto_lock_time):
        """Set the auto lock time."""
        if auto_lock_time < 1 or auto_lock_time > 15:
            auto_lock_time = 3
        self.set_int("auto-lock-time", auto_lock_time)
