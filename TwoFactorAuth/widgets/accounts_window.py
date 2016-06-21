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
from gi.repository import Gtk, Gio, Gdk, GObject, GLib
from TwoFactorAuth.widgets.accounts_list import AccountsList
from TwoFactorAuth.widgets.search_bar import SearchBar
from gettext import gettext as _
from hashlib import sha256
import logging


class AccountsWindow(Gtk.Box):

    def __init__(self, application, window):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.app = application
        self.window = window
        self.generate()

    def generate(self):
        self.generate_accounts_list()
        self.generate_search_bar()
        self.pack_start(self.search_bar, False, True, 0)
        self.pack_start(self.scrolled_win, True, True, 0)

    def generate_accounts_list(self):
        """
            Generate an account ListBox inside of a ScrolledWindow
        """
        self.accounts_list = AccountsList(self.app, self.window)
        self.scrolled_win = self.accounts_list.get_scrolled_win()

    def generate_search_bar(self):
        """
            Generate search bar box and entry
        """
        self.search_bar = SearchBar(self.accounts_list, self.window,
                                    self.window.hb.search_button)

    def get_accounts_list(self):
        return self.accounts_list

    def get_search_bar(self):
        return self.search_bar

    def toggle(self, visible):
        self.set_visible(visible)
        self.set_no_show_all(not visible)

    def is_visible(self):
        return self.get_visible()

    def hide(self):
        self.toggle(False)

    def show(self):
        self.toggle(True)
