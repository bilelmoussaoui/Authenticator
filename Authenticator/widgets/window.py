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
from gi.repository import Gtk, Gio, Gdk, GObject, GLib
from ..models import Logger, Settings, Database
from .headerbar import HeaderBar, HeaderBarState
from .inapp_notification import InAppNotification
from .accounts import AccountsList, AccountsListState, AddAcountWindow, EmptyAccountsList
from .search_bar import SearchBar
from .actions_bar import ActionsBar


class Window(Gtk.ApplicationWindow, GObject.GObject):
    """Main Window object."""
    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_LAST, None, (bool,))
    }

    # Default Window instance
    instance = None

    def __init__(self):
        Gtk.ApplicationWindow.__init__(self, type=Gtk.WindowType.TOPLEVEL)
        self.set_wmclass(
            "com.github.bilelmoussaoui.Authenticator", "Authenticator")
        self.set_icon_name("com.github.bilelmoussaoui.Authenticator")
        self.set_size_request(400, 600)
        self.resize(400, 600)
        self.restore_state()
        self._build_widgets()
        self.show_all()

    @staticmethod
    def get_default():
        """Return the default instance of Window."""
        if Window.instance is None:
            Window.instance = Window()
        return Window.instance

    def set_menu(self, gio_menu):
        """Set Headerbar popover menu."""
        HeaderBar.get_default().generate_popover_menu(gio_menu)

    def add_account(self, *args):
        add_window = AddAcountWindow()
        add_window.set_transient_for(self)
        add_window.show_all()
        add_window.present()

    def _do_update_view(self, *args):
        # FIXME: Don't use Database object here.
        headerbar = HeaderBar.get_default()
        count = Database.get_default().count
        if count != 0:
            child_name = "accounts-list"
            headerbar.set_state(HeaderBarState  .NORMAL)
        else:
            headerbar.set_state(HeaderBarState.EMPTY)
            child_name = "empty-accounts-list"
        child = self.main_stack.get_child_by_name(child_name)
        child.show_all()
        self.main_stack.set_visible_child(child)

    def toggle_select(self, *args):
        """
            Toggle select mode
        """
        if HeaderBar.get_default().state == HeaderBarState.NORMAL:
            HeaderBar.get_default().set_state(HeaderBarState.SELECT)
            AccountsList.get_default().set_state(AccountsListState.SELECT)
        else:
            HeaderBar.get_default().set_state(HeaderBarState.NORMAL)
            AccountsList.get_default().set_state(AccountsListState.NORMAL)

    def save_state(self):
        """Save window position & size."""
        settings = Settings.get_default()
        settings.window_position = self.get_position()

    def restore_state(self):
        """Restore the window's state."""
        settings = Settings.get_default()
        # Restore the window position
        position_x, position_y = settings.window_position
        if position_x != 0 and position_y != 0:
            self.move(position_x, position_y)
            Logger.debug("[Window] Restore postion x: {}, y: {}".format(position_x,
                                                                        position_y))
        else:
            # Fallback to the center
            self.set_position(Gtk.WindowPosition.CENTER)

    def _build_widgets(self):
        """Build main window widgets."""
        # HeaderBar
        headerbar = HeaderBar.get_default()
        # connect signals
        headerbar.select_btn.connect("clicked", self.toggle_select)
        headerbar.add_btn.connect("clicked", self.add_account)
        headerbar.cancel_btn.connect("clicked", self.toggle_select)

        self.set_titlebar(headerbar)

        # Main Container
        self.main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # In App Notifications
        # TODO: replace this with the gtk4 implementation
        self.notification = InAppNotification()
        self.main_container.pack_start(self.notification, False, False, 0)

        self.main_stack = Gtk.Stack()

        # Accounts List
        account_list_cntr = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        accounts_list = AccountsList.get_default()
        accounts_list.connect("changed", self._do_update_view)

        search_bar = SearchBar()
        search_bar.search_button = headerbar.search_btn
        search_bar.search_list = [accounts_list]

        actions_bar = ActionsBar.get_default()
        actions_bar.delete_btn.connect("clicked",
                                       accounts_list.delete_selected)
        accounts_list.connect("selected-count-rows-changed",
                              actions_bar.on_selected_rows_changed)

        account_list_cntr.pack_start(search_bar, False, False, 0)
        account_list_cntr.pack_start(accounts_list, True, True, 0)
        account_list_cntr.pack_start(actions_bar, False, False, 0)

        self.main_stack.add_named(account_list_cntr,
                                  "accounts-list")

        # Empty accounts list
        self.main_stack.add_named(EmptyAccountsList.get_default(),
                                  "empty-accounts-list")

        self.main_container.pack_start(self.main_stack, True, True, 0)
        self.add(self.main_container)
        self._do_update_view()

        actions_bar.bind_property("visible", headerbar.cancel_btn,
                                  "visible",
                                  GObject.BindingFlags.BIDIRECTIONAL)
        actions_bar.bind_property("no_show_all", headerbar.cancel_btn,
                                  "no_show_all",
                                  GObject.BindingFlags.BIDIRECTIONAL)
