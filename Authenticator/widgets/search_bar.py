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
from gi.repository import Gtk, GObject


class SearchBar(Gtk.SearchBar):
    """
        Search Bar widget.
    """
    _search_button = None

    def __init__(self, search_button=None, search_list=[]):
        Gtk.SearchBar.__init__(self)
        self.search_list = search_list
        self.search_entry = Gtk.SearchEntry()
        self.search_button = search_button
        self._build_widgets()

    @property
    def search_button(self):
        return self._search_button

    @search_button.setter
    def search_button(self, widget):
        if widget:
            self._search_button = widget
            self.bind_property("search-mode-enabled", self._search_button,
                               "active", GObject.BindingFlags.BIDIRECTIONAL)

    def _build_widgets(self):
        """
            Build the SearchBar widgets
        """
        self.set_show_close_button(True)

        self.search_entry.set_width_chars(28)
        self.search_entry.connect("search-changed",
                                  self.set_filter_func,
                                  self.filter_func)
        self.connect_entry(self.search_entry)
        self.add(self.search_entry)

    @staticmethod
    def filter_func(row, data, *_):
        """
            Filter function, used to check if the entered data exists on the application ListBox
        """
        data = data.lower()
        if len(data) > 0:
            return (
                data in row.account.username.lower()
                or
                data in row.account.provider.lower()
            )
        else:
            return True

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
