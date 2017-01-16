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
from Authenticator.const import settings
from Authenticator.widgets.change_password import PasswordWindow
from gettext import gettext as _
import logging


class SettingsWindow:

    def __init__(self, parent):
        self.parent = parent

        self.builder = Gtk.Builder.new_from_resource('/org/gnome/Authenticator/settings.ui')
        self.builder.connect_signals({
            "on_change_password" : self.__new_password_window,
            "on_activate_auto_lock" : self.__on_auto_lock_activated,
            "on_change_auto_lock_time" : self.__on_auto_lock_time_changed,
            "on_activate_password" : self.__on_password_activated,
            "on_key_press": self.__on_key_press,
            "on_activate_night_mode": self.__on_night_mode_activated,
            "on_close_window": self.close_window
        })
        self.window = self.builder.get_object("SettingsWindow")
        self.window.set_transient_for(self.parent)
        logging.debug("Settings Window created")

        self.auto_lock_check = self.builder.get_object("AutoLockCheck")
        self.auto_lock_spin = self.builder.get_object("AutoLockSpin")
        self.night_mode_check = self.builder.get_object("NightModeCheck")
        self.password_check = self.builder.get_object("PasswordCheck")
        self.password_button = self.builder.get_object("PasswordButton")
        # Restore settings
        _can_be_locked = settings.get_can_be_locked()
        _auto_lock_status = settings.get_auto_lock_status()
        _auto_lock_time = settings.get_auto_lock_time()
        _night_mode = settings.get_is_night_mode()

        self.night_mode_check.set_active(_night_mode)

        self.password_check.set_active(_can_be_locked)
        self.password_button.set_sensitive(_can_be_locked)

        self.auto_lock_check.set_sensitive(_can_be_locked)
        self.auto_lock_check.set_active(_can_be_locked)

        self.auto_lock_spin.set_sensitive(_auto_lock_status)
        self.auto_lock_spin.set_value(_auto_lock_time)

    def show_window(self):
        self.window.show_all()
        self.window.present()

    def __on_key_press(self, key, key_event):
        """
            Keyboard Listener handler
        """
        if Gdk.keyval_name(key_event.keyval).lower() == "escape":
            self.close_window()

    def __new_password_window(self, *args):
        """
            Show a new password window
        """
        pass_window = PasswordWindow(self.window)
        pass_window.show_window()

    def __on_auto_lock_time_changed(self, spin_button):
        """
            Update auto lock time
        """
        settings.set_auto_lock_time(spin_button.get_value_as_int())
        logging.info("Auto lock time updated")

    def __on_night_mode_activated(self, checkbutton, *args):
        checkbutton_status = checkbutton.get_active()
        settings.set_is_night_mode(checkbutton_status)
        Gtk.Settings.get_default().set_property(
            "gtk-application-prefer-dark-theme", checkbutton_status)

    def __on_password_activated(self, checkbutton, *args):
        """
            Update password state : enabled/disabled
        """
        checkbutton_status = checkbutton.get_active()
        self.password_button.set_sensitive(checkbutton_status)
        settings.set_is_locked(checkbutton_status)
        if checkbutton_status and not settings.is_password_set():
            self.__new_password_window()
        self.auto_lock_check.set_sensitive(checkbutton_status)
        logging.info("Password enabled/disabled")
        self.parent.emit("changed", True)

    def __on_auto_lock_activated(self, checkbutton, *args):
        """
            Update auto-lock state : enabled/disabled
        """
        checkbutton_status = checkbutton.get_active()
        self.auto_lock_spin.set_sensitive(checkbutton_status)
        settings.set_auto_lock_status(checkbutton_status)
        logging.info("Auto lock state updated")

    def close_window(self, *args):
        """
            Close the window
        """
        logging.debug("SettingsWindow closed")
        self.window.destroy()
