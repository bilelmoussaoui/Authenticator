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
from TwoFactorAuth.widgets.accounts_grid import AccountsGrid
from TwoFactorAuth.widgets.account_row import AccountRowGrid, AccountRowList
from TwoFactorAuth.widgets.search_bar import SearchBar
from TwoFactorAuth.models.account import Account
from gettext import gettext as _
from hashlib import sha256
import logging
from TwoFactorAuth.models.observer import Observer

class AccountsWindow(Gtk.Box, Observer):

    def __init__(self, application, window):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.app = application
        self.window = window
        self.scrolled_win = None
        self.generate()

    def generate(self):
        self.generate_accounts_list()
        self.generate_search_bar()
        self.pack_start(self.search_bar, False, True, 0)
        self.reorder_child(self.search_bar, 0)

    def generate_accounts_list(self):
        """
            Generate an account ListBox inside of a ScrolledWindow
        """
        apps = self.app.db.fetch_apps()
        count = len(apps)
        self.accounts = []
        for app in apps:
            account = Account(app, self.app.db)
            account.row_observerable.register(self)
            self.accounts.append(account)
            self.app.observable.register(account)

        self.accounts_list = AccountsList(self.window, self.accounts)
        self.accounts_grid = AccountsGrid(self.window, self.accounts)

        self.pack_start(self.accounts_list.get_scrolled_win(), True, True, 0)
        self.pack_start(self.accounts_grid.get_scrolled_win(), True, True, 0)
        is_grid = self.app.cfg.read(
            "view-mode", "preferences").lower() == "grid"
        self.set_mode_view(is_grid)

    def generate_search_bar(self):
        """
            Generate search bar box and entry
        """
        self.search_bar = SearchBar(self.window, self.window.hb.search_button,
                                    [self.accounts_list, self.accounts_grid])

    def update(self, *args, **kwargs):
        removed_id = kwargs.get("removed", None)
        if removed_id:
            self.accounts_list.remove_by_id(removed_id)
            self.accounts_grid.remove_by_id(removed_id)
        if self.app.db.count() == 0:
            self.window.refresh_window()

    def get_accounts_list(self):
        return self.accounts_list

    def get_accounts_grid(self):
        return self.accounts_grid

    def set_mode_view(self, is_grid):
        if is_grid:
            self.scrolled_win = self.accounts_grid.get_scrolled_win()
            self.accounts_list.get_scrolled_win().set_visible(False)
            self.accounts_list.get_scrolled_win().set_no_show_all(True)
            self.accounts_grid.refresh()
        else:
            self.scrolled_win = self.accounts_list.get_scrolled_win()
            self.accounts_grid.get_scrolled_win().set_no_show_all(True)
            self.accounts_grid.get_scrolled_win().set_visible(False)
            self.accounts_list.refresh()
        self.scrolled_win.set_no_show_all(False)
        self.scrolled_win.set_visible(True)

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

    def refresh(self, *args):
        self.accounts_list.refresh()
        self.accounts_grid.refresh()

    def append(self, app):
        """
            Add an element to the ListBox
        """
        app[2] = sha256(app[2].encode('utf-8')).hexdigest()
        account = Account(app, self.app.db)
        account.row_observerable.register(self)
        self.accounts.append(account)
        self.app.observable.register(account)
        self.accounts_list.add(AccountRowList(self.accounts_list, self.window, account))
        self.accounts_grid.add(AccountRowGrid(self.accounts_grid, self.window, account))
        self.show_all()
