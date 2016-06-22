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
from gi.repository import Gtk, Gio, Gdk
import logging


class SearchBar(Gtk.Revealer):

    def __init__(self, listbox, window, search_button):
        self.search_entry = Gtk.SearchEntry()
        self.listbox = listbox
        self.search_button = search_button
        self.window = window
        self.generate()
        self.search_button.connect("toggled", self.toggle)
        self.window.connect("key-press-event", self.__on_key_press)

    def generate(self):
        Gtk.Revealer.__init__(self)
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self.search_entry.set_width_chars(28)
        self.search_entry.connect("search-changed", self.filter_applications)

        box.pack_start(self.search_entry, True, False, 12)
        box.props.margin = 6

        self.add(box)
        self.set_reveal_child(False)

    def toggle(self, *args):
        if self.is_visible():
            self.set_reveal_child(False)
            self.search_entry.set_text("")
            self.listbox.set_filter_func(lambda x, y, z: True,
                                         None, False)
        else:
            self.set_reveal_child(True)
            self.focus()

    def filter_func(self, row, data, notify_destroy):
        """
            Filter function, used to check if the entered data exists on the application ListBox
        """
        app_label = row.get_name()
        data = data.lower()
        if len(data) > 0:
            return data in app_label.lower()
        else:
            return True

    def __on_key_press(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval).lower()
        if keyname == 'escape' and self.search_button.get_active():
            if self.search_entry.is_focus():
                self.search_button.set_active(False)
                self.search_entry.set_text("")
            else:
                self.focus()

        if not "is_locked" in dir(self.window) or not self.window.is_locked():
            if keyname == "backspace":
                if self.is_empty() and self.is_visible():
                    self.search_button.set_active(False)
                    return True

            if event.state & Gdk.ModifierType.CONTROL_MASK:
                if keyname == 'f':
                    self.search_button.set_active(
                        not self.search_button.get_active())
                    return True
        return False

    def focus(self):
        self.search_entry.grab_focus_without_selecting()

    def is_visible(self):
        return self.get_reveal_child()

    def is_empty(self):
        return len(self.search_entry.get_text()) == 0

    def filter_applications(self, entry):
        data = entry.get_text().strip()
        self.listbox.set_filter_func(self.filter_func, data, False)
