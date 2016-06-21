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
from gi.repository import Gtk, Gio
from TwoFactorAuth.utils import is_gnome
import logging
from gettext import gettext as _


class HeaderBar(Gtk.HeaderBar):

    search_button = Gtk.ToggleButton()
    add_button = Gtk.Button()
    settings_button = Gtk.Button()
    remove_button = Gtk.Button()
    cancel_button = Gtk.Button()
    select_button = Gtk.Button()
    lock_button = Gtk.Button()

    popover = None

    def __init__(self, app, window):
        self.app = app
        self.window = window
        Gtk.HeaderBar.__init__(self)
        self.generate()

    def generate(self):
        self.set_show_close_button(True)
        right_box = self.generate_right_box()
        left_box = self.generate_left_box()

        if not is_gnome():
            # add settings menu
            self.generate_popover(right_box)

        self.pack_start(left_box)
        self.pack_end(right_box)

    def generate_left_box(self):
        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        remove_icon = Gio.ThemedIcon(name="user-trash-symbolic")
        remove_image = Gtk.Image.new_from_gicon(
            remove_icon, Gtk.IconSize.BUTTON)
        self.remove_button.set_tooltip_text(_("Remove selected accounts"))
        self.remove_button.set_image(remove_image)
        self.remove_button.set_sensitive(False)
        self.toggle_remove_button(False)

        add_icon = Gio.ThemedIcon(name="list-add-symbolic")
        add_image = Gtk.Image.new_from_gicon(add_icon, Gtk.IconSize.BUTTON)
        self.add_button.set_tooltip_text(_("Add a new account"))
        self.add_button.set_image(add_image)

        pass_enabled = self.app.cfg.read("state", "login")
        can_be_locked = not self.app.locked and pass_enabled
        lock_icon = Gio.ThemedIcon(name="changes-prevent-symbolic")
        lock_image = Gtk.Image.new_from_gicon(lock_icon, Gtk.IconSize.BUTTON)
        self.lock_button.set_tooltip_text(_("Lock the Application"))
        self.lock_button.set_image(lock_image)
        self.toggle_lock_button(can_be_locked)

        left_box.add(self.remove_button)
        left_box.add(self.add_button)
        left_box.add(self.lock_button)
        return left_box

    def generate_right_box(self):
        count = self.app.db.count()

        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        select_icon = Gio.ThemedIcon(name="object-select-symbolic")
        select_image = Gtk.Image.new_from_gicon(
            select_icon, Gtk.IconSize.BUTTON)
        self.select_button.set_tooltip_text(_("Selection mode"))
        self.select_button.set_image(select_image)
        self.toggle_select_button(count > 0)

        search_icon = Gio.ThemedIcon(name="system-search-symbolic")
        search_image = Gtk.Image.new_from_gicon(
            search_icon, Gtk.IconSize.BUTTON)
        self.search_button.set_tooltip_text(_("Search"))
        self.search_button.set_image(search_image)
        self.toggle_search_button(count > 0)

        self.cancel_button.set_label(_("Cancel"))
        self.toggle_cancel_button(False)

        right_box.add(self.search_button)
        right_box.add(self.select_button)
        right_box.add(self.cancel_button)
        return right_box

    def generate_popover(self, box):
        settings_icon = Gio.ThemedIcon(name="open-menu-symbolic")
        settings_image = Gtk.Image.new_from_gicon(
            settings_icon, Gtk.IconSize.BUTTON)
        self.settings_button.set_tooltip_text(_("Settings"))
        self.settings_button.set_image(settings_image)
        self.settings_button.connect("clicked", self.toggle_popover)

        self.popover = Gtk.Popover.new_from_model(
            self.settings_button, self.app.menu)
        self.popover.props.width_request = 200
        box.add(self.settings_button)

    def toggle_popover(self, *args):
        if self.popover:
            if self.popover.get_visible():
                self.popover.hide()
            else:
                self.popover.show_all()

    def toggle_select_mode(self):
        is_select_mode = self.window.is_select_mode
        pass_enabled = self.app.cfg.read("state", "login")

        self.toggle_remove_button(is_select_mode)
        self.toggle_cancel_button(is_select_mode)
        self.set_show_close_button(not is_select_mode)
        self.toggle_settings_button(not is_select_mode)

        self.toggle_lock_button(not is_select_mode and pass_enabled)
        self.toggle_add_button(not is_select_mode)
        self.toggle_select_button(not is_select_mode)

        if is_select_mode:
            self.get_style_context().add_class("selection-mode")
        else:
            self.get_style_context().remove_class("selection-mode")

    def toggle_search(self):
        self.search_button.set_active(not self.search_button.get_active())

    def toggle_search_button(self, visible):
        self.search_button.set_visible(visible)
        self.search_button.set_no_show_all(not visible)

    def toggle_select_button(self, visible):
        self.select_button.set_visible(visible)
        self.select_button.set_no_show_all(not visible)

    def toggle_settings_button(self, visible):
        if not is_gnome():
            self.settings_button.set_visible(visible)
            self.settings_button.set_no_show_all(not visible)

    def toggle_lock_button(self, visible):
        self.lock_button.set_visible(visible)
        self.lock_button.set_no_show_all(not visible)

    def toggle_add_button(self, visible):
        self.add_button.set_visible(visible)
        self.add_button.set_no_show_all(not visible)

    def toggle_cancel_button(self, visible):
        self.cancel_button.set_visible(visible)
        self.cancel_button.set_no_show_all(not visible)

    def toggle_remove_button(self, visible):
        self.remove_button.set_visible(visible)
        self.remove_button.set_no_show_all(not visible)

    def hide(self):
        self.toggle_add_button(False)
        self.toggle_lock_button(False)
        self.toggle_cancel_button(False)
        self.toggle_remove_button(False)
        self.toggle_search_button(False)
        self.toggle_settings_button(True)
        self.toggle_select_button(False)

    def refresh(self):
        is_locked = self.app.locked
        pass_enabled = self.app.cfg.read("state", "login")
        can_be_locked = not is_locked and pass_enabled
        count = self.app.db.count()
        if is_locked:
            self.hide()
        else:
            if count == 0:
                self.toggle_add_button(True)
                self.toggle_select_button(False)
                self.toggle_remove_button(False)
                self.toggle_search_button(False)
                self.toggle_lock_button(can_be_locked)
                self.toggle_settings_button(True)
                self.toggle_cancel_button(False)
            else:
                self.toggle_add_button(True)
                self.toggle_select_button(True)
                self.toggle_remove_button(False)
                self.toggle_search_button(True)
                self.toggle_lock_button(can_be_locked)
                self.toggle_settings_button(True)
                self.toggle_cancel_button(False)
