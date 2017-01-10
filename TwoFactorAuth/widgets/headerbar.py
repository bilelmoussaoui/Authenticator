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
from TwoFactorAuth.utils import show_app_menu
import logging
from gettext import gettext as _

# view-grid-symbolic
# view-list-symoblic
class HeaderBar(Gtk.HeaderBar):
    search_button = Gtk.ToggleButton()
    add_button = Gtk.Button()
    view_mode_button = Gtk.Button()
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

        if show_app_menu():
            # add settings menu
            self.generate_popover(right_box)

        self.pack_start(left_box)
        self.pack_end(right_box)
        self.refresh()

    def generate_left_box(self):
        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        remove_icon = Gio.ThemedIcon(name="user-trash-symbolic")
        remove_image = Gtk.Image.new_from_gicon(
            remove_icon, Gtk.IconSize.BUTTON)
        self.remove_button.set_tooltip_text(_("Remove selected accounts"))
        self.remove_button.set_image(remove_image)
        self.remove_button.set_sensitive(False)

        add_icon = Gio.ThemedIcon(name="list-add-symbolic")
        add_image = Gtk.Image.new_from_gicon(add_icon, Gtk.IconSize.BUTTON)
        self.add_button.set_tooltip_text(_("Add a new account"))
        self.add_button.set_image(add_image)

        lock_icon = Gio.ThemedIcon(name="changes-prevent-symbolic")
        lock_image = Gtk.Image.new_from_gicon(lock_icon, Gtk.IconSize.BUTTON)
        self.lock_button.set_tooltip_text(_("Lock the Application"))
        self.lock_button.set_image(lock_image)


        left_box.add(self.remove_button)
        left_box.add(self.add_button)
        left_box.add(self.lock_button)
        return left_box

    def generate_right_box(self):
        count = self.app.db.count()
        is_grid = self.app.cfg.read("view-mode", "preferences").lower() == "grid"
        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        select_icon = Gio.ThemedIcon(name="object-select-symbolic")
        select_image = Gtk.Image.new_from_gicon(
            select_icon, Gtk.IconSize.BUTTON)
        self.select_button.set_tooltip_text(_("Selection mode"))
        self.select_button.set_image(select_image)

        search_icon = Gio.ThemedIcon(name="system-search-symbolic")
        search_image = Gtk.Image.new_from_gicon(
            search_icon, Gtk.IconSize.BUTTON)
        self.search_button.set_tooltip_text(_("Search"))
        self.search_button.set_image(search_image)
        self.search_button.set_visible(count > 0)

        self.set_toggle_view_mode_icon(is_grid)
        self.view_mode_button.connect("clicked", self.toggle_view_mode)

        self.cancel_button.set_label(_("Cancel"))

        right_box.add(self.search_button)
        right_box.add(self.view_mode_button)
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

    def toggle_view_mode(self, *args):
        is_grid = self.app.cfg.read("view-mode", "preferences").lower() == "grid"
        if not is_grid:
            self.app.cfg.update("view-mode", "grid" , "preferences")
        else:
            self.app.cfg.update("view-mode", "list" , "preferences")
        self.set_toggle_view_mode_icon(not is_grid)
        self.window.toggle_view_mode(not is_grid)

    def set_toggle_view_mode_icon(self, is_grid):
        if not is_grid:
            view_mode_icon = Gio.ThemedIcon(name="view-grid-symbolic")
            self.view_mode_button.set_tooltip_text(_("Grid mode"))
        else:
            view_mode_icon = Gio.ThemedIcon(name="view-list-symbolic")
            self.view_mode_button.set_tooltip_text(_("List mode"))
        view_mode_image = Gtk.Image.new_from_gicon(view_mode_icon, Gtk.IconSize.BUTTON)
        self.view_mode_button.set_image(view_mode_image)

    def toggle_select_mode(self):
        is_select_mode = self.window.is_select_mode
        pass_enabled = self.app.cfg.read("state", "login")

        self.remove_button.set_visible(is_select_mode)
        self.cancel_button.set_visible(is_select_mode)
        self.set_show_close_button(not is_select_mode)
        self.settings_button.set_visible(not is_select_mode)

        self.lock_button.set_visible(not is_select_mode and pass_enabled)
        self.add_button.set_visible(not is_select_mode)
        self.select_button.set_visible(not is_select_mode)

        if is_select_mode:
            self.get_style_context().add_class("selection-mode")
        else:
            self.get_style_context().remove_class("selection-mode")

    def toggle_search(self):
        self.search_button.set_active(not self.search_button.get_active())

    def toggle_settings_button(self, visible):
        if show_app_menu():
            self.settings_button.set_visible(visible)
            self.settings_button.set_no_show_all(not visible)


    def refresh(self):
        is_locked = self.app.locked
        pass_enabled = self.app.cfg.read("state", "login")
        can_be_locked = not is_locked and pass_enabled
        count = self.app.db.count()
        self.view_mode_button.set_visible(not count == 0 and not is_locked)
        self.select_button.set_visible(not count == 0 and not is_locked)
        self.search_button.set_visible(not count == 0 and not is_locked)
        self.view_mode_button.set_no_show_all(not (not count == 0 and not is_locked))
        self.select_button.set_no_show_all(not(not count == 0 and not is_locked))
        self.search_button.set_no_show_all(not(not count == 0 and not is_locked))
        self.lock_button.set_visible(can_be_locked)
        self.add_button.set_visible(not is_locked)
        self.lock_button.set_no_show_all(not can_be_locked)
        self.add_button.set_no_show_all(is_locked)

        self.toggle_settings_button(True)
        self.cancel_button.set_visible(False)
        self.remove_button.set_visible(False)
        self.cancel_button.set_no_show_all(True)
        self.remove_button.set_no_show_all(True)
