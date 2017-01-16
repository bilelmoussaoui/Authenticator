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
import logging
from Authenticator.const import settings
from Authenticator.models.account import Account
from Authenticator.models.observer import Observer
from Authenticator.widgets.account_row import AccountRowGrid, AccountRowList
from Authenticator.widgets.accounts import AccountsGrid, AccountsList
from Authenticator.widgets.search_bar import SearchBar
from gettext import gettext as _
from gi.repository import GLib, GObject, Gdk, Gio, Gtk
from hashlib import sha256


class AccountsWindow(Gtk.Box, Observer):

    def __init__(self, application, window):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.app = application
        self.window = window
        self.generate()

    def generate(self):
        self.stack = Gtk.Stack()
        self.scrolled_win = Gtk.ScrolledWindow()
        self.stack.set_vexpand(False)
        self.stack.set_hexpand(False)
        self.stack.set_transition_duration(400)
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

        self.generate_accounts_list()
        self.generate_search_bar()

    def generate_accounts_list(self):
        """
            Generate an account ListBox inside of a ScrolledWindow
        """
        apps = self.app.db.fetch_apps()
        count = len(apps)
        self.scrolled_win = Gtk.ScrolledWindow()
        self.accounts = []
        for app in apps:
            account = Account(app, self.app.db)
            account.row_observerable.register(self)
            self.accounts.append(account)
            self.app.observable.register(account)

        self.accounts_list = AccountsList(self.window, self.accounts)
        self.accounts_grid = AccountsGrid(self.window, self.accounts)

        self.stack.add_named(self.accounts_list, "list")
        self.stack.add_named(self.accounts_grid, "grid")
        self.scrolled_win.add_with_viewport(self.stack)

        self.pack_start(self.scrolled_win, True, True, 0)
        self.set_mode_view(settings.get_view_mode(), True)

    def generate_search_bar(self):
        """
            Generate search bar box and entry
        """
        self.search_bar = SearchBar(self.window, self.window.hb.search_button,
                                    [self.accounts_list, self.accounts_grid])
        self.pack_start(self.search_bar, False, True, 0)
        self.reorder_child(self.search_bar, 0)

    def update(self, *args, **kwargs):
        removed_id = kwargs.get("removed", None)
        unlocked = kwargs.pop("unlocked", None)
        locked = kwargs.pop("locked", None)
        counter = kwargs.pop("counter", None)
        view_mode = kwargs.pop("view_mode", None)
        if counter == 0 or locked:
            self.set_visible(False)
            self.set_no_show_all(True)
        elif unlocked or counter != 0:
            self.set_visible(True)
            self.set_no_show_all(False)
        if removed_id:
            self.accounts_list.remove_by_id(removed_id)
            self.accounts_grid.remove_by_id(removed_id)
            self.window.emit("changed", True)
        if view_mode:
            self.set_mode_view(view_mode)

    def get_accounts_list(self):
        return self.accounts_list

    def get_accounts_grid(self):
        return self.accounts_grid

    def set_mode_view(self, view_mode, on_start=False):
        self.stack.set_visible_child_name(view_mode)
        if not on_start:
            settings.set_view_mode(view_mode)

    def get_search_bar(self):
        return self.search_bar

    def append(self, app):
        """
            Add an element to the ListBox
        """
        if app:
            account = Account(app, self.app.db)
            account.row_observerable.register(self)
            self.accounts.append(account)
            self.app.observable.register(account)
            self.accounts_list.append(account)
            self.accounts_grid.append(account)
            self.window.emit("changed", True)
