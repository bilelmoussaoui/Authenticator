from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, Gdk, GObject, GLib
from TwoFactorAuth.widgets.accounts_list import AccountsList
from TwoFactorAuth.widgets.search_bar import SearchBar
import logging
from gettext import gettext as _
from hashlib import sha256

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
