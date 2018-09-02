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
from gettext import gettext as _

from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject, Gio

from .row import AccountRow
from ...models import Database, Account, Keyring


class AccountsListState:
    NORMAL = 0
    SELECT = 1


class AccountsList(Gtk.ListBox, GObject.GObject):
    """Accounts List."""

    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_LAST, None, (bool,)),
        'selected-count-rows-changed': (GObject.SignalFlags.RUN_LAST, None, (int, )),
        'account-deleted': (GObject.SignalFlags.RUN_LAST, None, ()),
    }
    # Default instance of accounts list
    instance = None

    def __init__(self):
        GObject.GObject.__init__(self)
        Gtk.ListBox.__init__(self)
        self.set_selection_mode(Gtk.SelectionMode.NONE)
        self.get_style_context().add_class("applications-list")
        self.state = AccountsListState.NORMAL
        self.__fill_data()

    @staticmethod
    def get_default():
        """Return the default instance of AccountsList."""
        if AccountsList.instance is None:
            AccountsList.instance = AccountsList()
        return AccountsList.instance

    def __fill_data(self):
        """Fill the Accounts List with accounts."""
        accounts = Database.get_default().accounts
        for account in accounts:
            _id = account["id"]
            name = account["name"]
            provider = account["provider"]
            secret_id = account["secret_id"]
            logo = account["logo"]
            row = AccountRow(Account(_id, name, provider, secret_id, logo))
            row.connect("on_selected", self.on_row_checked)
            self.add(row)

    def append(self, name, provider, secret_id, logo):
        account = Account.create(name, provider, secret_id, logo)
        row = AccountRow(account)
        row.connect("on_selected", self.on_row_checked)
        self.add(row)
        self.emit("changed", True)

    def delete(self, row):
        # Remove an account from the list
        self.emit("changed", False)

    def on_row_checked(self, row):
        count_selected_rows = 0
        for _row in self.get_children():
            if _row.check_btn.props.active:
                count_selected_rows += 1
        self.emit("selected-count-rows-changed", count_selected_rows)

    def set_state(self, state):
        show_check_btn = (state == AccountsListState.SELECT)
        for child in self.get_children():
            child.check_btn.set_visible(show_check_btn)
            child.check_btn.set_no_show_all(not show_check_btn)

    def delete_selected(self, *args):
        for child in self.get_children():
            check_btn = child.check_btn
            if check_btn.props.active:
                child.account.remove()
                self.remove(child)
        self.emit("account-deleted")
        self.set_state(AccountsListState.NORMAL)


class EmptyAccountsList(Gtk.Box):
    """
        Empty accounts list.
    """
    instance = None

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self._build_widgets()

    @staticmethod
    def get_default():
        if not EmptyAccountsList.instance:
            EmptyAccountsList.instance = EmptyAccountsList()
        return EmptyAccountsList.instance

    def _build_widgets(self):
        """Build widgets."""
        self.set_border_width(18)
        self.set_valign(Gtk.Align.CENTER)
        self.set_halign(Gtk.Align.CENTER)

        # Image
        gicon = Gio.ThemedIcon(name="dialog-information-symbolic")
        img = Gtk.Image.new_from_gicon(gicon, Gtk.IconSize.DIALOG)

        # Label
        label = Gtk.Label(label=_("There's no account yet..."))

        self.pack_start(img, False, False, 6)
        self.pack_start(label, False, False, 6)
