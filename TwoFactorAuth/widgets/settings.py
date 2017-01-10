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
from TwoFactorAuth.models.settings import SettingsReader
from TwoFactorAuth.widgets.change_password import PasswordWindow
from gettext import gettext as _
import logging

class SettingsWindow(Gtk.Window):
    main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

    def __init__(self, parent):
        self.parent = parent
        self.cfg = SettingsReader()
        self.auto_lock_time = Gtk.SpinButton()
        self.enable_switch = Gtk.CheckButton()
        self.auto_lock_switch = Gtk.CheckButton()
        self.password_button = Gtk.Button()
        self.hb = Gtk.HeaderBar()
        self.generate_window()
        self.generate_components()

    def generate_window(self):
        Gtk.Window.__init__(self, title=_("Settings"), type=Gtk.WindowType.TOPLEVEL,
                            destroy_with_parent=True, modal=True)
        self.connect("delete-event", self.close_window)
        self.resize(400, 300)
        self.set_size_request(400, 300)
        self.set_border_width(18)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_transient_for(self.parent)
        self.connect("key_press_event", self.on_key_press)
        self.hb.set_show_close_button(True)
        self.set_titlebar(self.hb)
        self.add(self.main_box)


    def show_window(self):
        self.show_all()

    def on_key_press(self, key, key_event):
        """
            Keyboard Listener handler
        """
        if Gdk.keyval_name(key_event.keyval) == "Escape":
            self.close_window()

    def generate_components(self):
        """
            Generate all the components
        """
        self.stack = Gtk.Stack()
        self.stack.set_vexpand(True)
        self.stack.set_hexpand(True)
        self.stack.set_transition_type(
            Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(1000)

        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(self.stack)
        self.hb.set_custom_title(stack_switcher)

        behavior_settings = self.generate_behavior_settings()
        account_settings = self.generate_account_settings()
        self.stack.add_titled(behavior_settings, "behavior", _("Behavior"))
        self.stack.add_titled(account_settings, "account", _("Account"))
        self.main_box.add(self.stack)

    def generate_account_settings(self):
        """
            Create a box with login settings components
            :return (Gtk.Box): Box contains all the components
        """
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        password_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        lock_enabled = bool(self.cfg.read("state", "login"))
        self.enable_switch.set_active(lock_enabled)
        self.enable_switch.connect("toggled", self.on_switch_activated)

        password_label = Gtk.Label()
        password_label.set_label(_("Password protection"))

        self.password_button.get_style_context().add_class("flat")
        self.password_button.get_style_context().add_class("text-button")
        self.password_button.set_label("******")
        self.password_button.connect("clicked", self.new_password_window)
        self.password_button.set_sensitive(lock_enabled)

        password_box.pack_start(self.enable_switch, False, True, 6)
        password_box.pack_start(password_label, False, True, 6)
        password_box.pack_start(self.password_button, False, True, 6)

        main_box.pack_start(password_box, False, True, 6)
        return main_box

    def generate_behavior_settings(self):
        """
            Create a box with user settings components
            :return (Gtk.Box): Box contains all the components
        """
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        is_auto_lock_active = bool(self.cfg.read("auto-lock", "preferences"))
        auto_lock_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        auto_lock_label = Gtk.Label().new(_("Auto-lock the application (m):"))
        self.auto_lock_switch.set_sensitive(self.cfg.read("state", "login"))
        self.auto_lock_switch.set_active(is_auto_lock_active)
        self.auto_lock_switch.connect("toggled", self.on_auto_lock_activated)

        default_value = self.cfg.read("auto-lock-time", "preferences")
        if default_value < 1 or default_value > 10:
            default_value = 3
        adjustment = Gtk.Adjustment(value=default_value, lower=1, upper=10,
                                    step_increment=1, page_increment=1, page_size=0)
        self.auto_lock_time.connect(
            "value-changed", self.on_auto_lock_time_changed)
        self.auto_lock_time.set_adjustment(adjustment)
        self.auto_lock_time.set_sensitive(is_auto_lock_active)
        self.auto_lock_time.set_value(default_value)

        auto_lock_box.pack_start(self.auto_lock_switch, False, True, 6)
        auto_lock_box.pack_start(auto_lock_label, False, True, 6)
        auto_lock_box.pack_start(self.auto_lock_time, False, True, 12)

        main_box.pack_start(auto_lock_box, False, True, 6)
        return main_box

    def new_password_window(self, *args):
        """
            Show a new password window
        """
        pass_window = PasswordWindow(self)
        pass_window.show_window()

    def on_auto_lock_time_changed(self, spin_button):
        """
            Update auto lock time
        """
        self.cfg.update("auto-lock-time",
                        spin_button.get_value_as_int(), "preferences")
        logging.info("Auto lock time updated")

    def on_switch_activated(self, switch, *args):
        """
            Update password state : enabled/disabled
        """
        self.password_button.set_sensitive(switch.get_active())
        self.cfg.update("state", switch.get_active(), "login")
        if switch.get_active():
            password = self.cfg.read("password", "login")
            if len(password) == 0:
                self.new_password_window()
        self.auto_lock_switch.set_sensitive(switch.get_active())
        logging.info("Password enabled/disabled")
        self.parent.refresh_window()

    def on_auto_lock_activated(self, switch, *args):
        """
            Update auto-lock state : enabled/disabled
        """
        self.auto_lock_time.set_sensitive(switch.get_active())
        self.cfg.update("auto-lock", switch.get_active(), "preferences")
        logging.info("Auto lock state updated")

    def close_window(self, *args):
        """
            Close the window
        """
        logging.debug("SettingsWindow closed")
        self.destroy()
