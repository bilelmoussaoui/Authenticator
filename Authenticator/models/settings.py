"""
 Copyright © 2017 Bilal Elmoussaoui <bil.elmoussaoui@gmail.com>

 This file is part of Authenticator.

 Authenticator is free software: you can redistribute it and/or
 modify it under the terms of the GNU General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 Authenticator is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Authenticator. If not, see <http://www.gnu.org/licenses/>.
"""
from gi.repository import Gio, GLib

from .logger import Logger


class Settings(Gio.Settings):
    """Settings handler."""
    # Default Settings instance
    instance = None

    def __init__(self):
        Gio.Settings.__init__(self)

    @staticmethod
    def new():
        """Create a new Settings object"""
        g_settings = Gio.Settings.new(
            "com.github.bilelmoussaoui.Authenticator")
        g_settings.__class__ = Settings
        return g_settings

    @staticmethod
    def get_default():
        """Return the default instance of Settings."""
        if Settings.instance is None:
            Settings.instance = Settings.new()
        return Settings.instance

    @property
    def window_position(self):
        """Return the window's position."""
        return tuple(self.get_value('window-position'))

    @window_position.setter
    def window_position(self, position):
        """Set the window position."""
        position = GLib.Variant('ai', list(position))
        self.set_value('window-position', position)

    @property
    def is_night_mode(self):
        """Is night mode?"""
        return self.get_boolean('night-mode')

    @is_night_mode.setter
    def is_night_mode(self, status):
        """Set the night mode."""
        self.set_boolean('night-mode', status)

    @property
    def window_maximized(self):
        """Was the window maximized?."""
        return self.get_boolean("is-maximized")

    @window_maximized.setter
    def window_maximized(self, is_maximized):
        self.set_boolean("is-maximized", is_maximized)
