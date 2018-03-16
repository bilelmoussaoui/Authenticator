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
from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, Gdk
from ..models import Settings


class SearchBar(Gtk.Revealer):
    """
        Search Bar widget.
    """

    def __init__(self, search_button=None, search_list=[]):
        self.search_entry = Gtk.SearchEntry()
        self.search_list = search_list
        self.search_button = search_button
        self._build_widgets()

    @property
    def search_list(self):
        return self._search_list

    @search_list.setter
    def search_list(self, value):
        if value:
            self._search_list = value

    @property
    def search_button(self):
        return self._search_button

    @search_button.setter
    def search_button(self, widget):
        if widget:
            self._search_button = widget
            self._search_button.connect("toggled",
                                        self.toggle)

    def _build_widgets(self):
        """
            Build the search bar widgets
        """
        Gtk.Revealer.__init__(self)
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self.search_entry.set_width_chars(28)
        self.search_entry.connect("search-changed",
                                  self.set_filter_func,
                                  self.filter_func)

        box.pack_start(self.search_entry, True, False, 12)

        self.add(box)
        self.set_reveal_child(False)

    def toggle(self, *args):
        if self.is_visible():
            self.search_entry.set_text("")
            self.set_reveal_child(False)

            def filter_func(*args):
                return True
            self.set_filter_func(self.search_entry, filter_func)
        else:
            self.set_reveal_child(True)
            self.focus()

    @staticmethod
    def filter_func(row, data, *args):
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
        key_name = Gdk.keyval_name(event.keyval).lower()
        is_activez = self.search_button.get_active()
        if key_name == 'escape' and is_active:
            if self.search_entry.is_focus():
                self.search_button.set_active(False)
                self.search_entry.set_text("")
            else:
                self.focus()

        if not Settings.get_default().is_locked:
            if key_name == "backspace":
                if self.is_empty() and self.is_visible():
                    self.search_button.set_active(False)
                    return True

            if event.state & Gdk.ModifierType.CONTROL_MASK:
                if key_name == 'f':
                    self.search_button.set_active(is_active)
                    return True
        return False

    def focus(self):
        """Focus the search bar entry"""
        self.search_entry.grab_focus_without_selecting()

    def is_visible(self):
        """Return the search bar's visibility"""
        return self.get_reveal_child()

    def is_empty(self):
        """Return if the search entry has any text on it."""
        return len(self.search_entry.get_text()) == 0

    def set_filter_func(self, entry, filter_func):
        """
        Filter the data of a listbox from an entry
        :param entry: Gtk.Entry
        :param filter_func: The function to use as filter
        """
        data = entry.get_text().strip()
        for search_list in self.search_list:
            search_list.set_filter_func(filter_func,
                                        data, False)
