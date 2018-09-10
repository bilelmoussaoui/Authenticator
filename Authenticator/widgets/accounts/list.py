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
from ...models import Database, Account, AccountsManager
from ...utils import load_pixbuf_from_provider


class AccountsWidget(Gtk.Box, GObject.GObject):
    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_LAST, None, ()),
        'selected-rows-changed': (GObject.SignalFlags.RUN_LAST, None, (int,)),
    }
    instance = None

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        GObject.GObject.__init__(self)
        self.get_style_context().add_class("accounts-widget")

        self._providers = {}
        self._to_delete = []
        self._build_widgets()
        self.__fill_data()

    def _build_widgets(self):
        self.otp_progress_bar = Gtk.ProgressBar()
        self.add(self.otp_progress_bar)
        AccountsManager.get_default().connect("counter_updated", self._on_counter_updated)

        self.accounts_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.accounts_container.get_style_context().add_class("accounts-container")
        accounts_scrolled = Gtk.ScrolledWindow()
        accounts_scrolled.add_with_viewport(self.accounts_container)
        self.pack_start(accounts_scrolled, True, True, 0)

    @staticmethod
    def get_default():
        """Return the default instance of AccountsWidget."""
        if AccountsWidget.instance is None:
            AccountsWidget.instance = AccountsWidget()
        return AccountsWidget.instance

    def append(self, username, provider, token, _id=None):
        accounts_list = self._providers.get(provider)
        if not accounts_list:
            accounts_list = AccountsList()
            accounts_list.connect("selected-count-rows-changed",
                                  self._on_selected_count_changed)
            accounts_list.connect("account-deleted", self._on_account_deleted)
            self._providers[provider] = accounts_list
            provider_widget = ProviderWidget(accounts_list, provider)
            self.accounts_container.pack_start(provider_widget, False, False, 0)
        if not _id:
            accounts_list.append_new(username, provider, token)
            self._reorder()
        else:
            accounts_list.append(_id, username, provider, token)
        self.emit("changed")

    @property
    def accounts_lists(self):
        return self._providers.values()

    def set_state(self, state):
        for account_list in self._providers.values():
            account_list.set_state(state)

    def delete_selected(self, *_):
        for account_list in self._providers.values():
            account_list.delete_selected()
        self._clean_unneeded_providers_widgets()
        self.emit("changed")

    def update_provider(self, account, new_provider):
        current_account_list = None
        account_row = None
        for account_list in self._providers.values():
            for account_row in account_list:
                if account_row.account == account:
                    current_account_list = account_list
                    break

            if current_account_list:
                break
        if account_row:
            current_account_list.remove(account_row)
            self.append(account_row.account.username,
                        new_provider,
                        account_row.account.secret_id,
                        account_row.account.id)
        self._on_account_deleted(current_account_list)
        self._reorder()
        self._clean_unneeded_providers_widgets()

    def __fill_data(self):
        """Fill the Accounts List with accounts."""
        accounts = Database.get_default().accounts
        for account in accounts:
            _id = account["id"]
            username = account["username"]
            provider = account["provider"]
            secret_id = account["secret_id"]

            self.append(username, provider, secret_id, _id)

    def _on_selected_count_changed(self, *_):
        total_selected_rows = 0
        for account_list in self._providers.values():
            total_selected_rows += account_list.selected_rows_count
        self.emit("selected-rows-changed", total_selected_rows)

    def _on_account_deleted(self, account_list):
        if len(account_list.get_children()) == 0:
            self._to_delete.append(account_list)

    def _clean_unneeded_providers_widgets(self):
        for account_list in self._to_delete:
            provider_widget = account_list.get_parent()
            self.accounts_container.remove(provider_widget)
            del self._providers[provider_widget.provider]
        self._to_delete = []

    def _reorder(self):
        """
            Re-order the ProviderWidget on AccountsWidget.
        """
        childes = self.accounts_container.get_children()
        ordered_childes = sorted(childes, key=lambda children: children.provider.lower())
        for i in range(len(ordered_childes)):
            self.accounts_container.reorder_child(ordered_childes[i], i)
        self.show_all()

    def _on_counter_updated(self, accounts_manager, counter):
        counter_fraction = int(counter) / accounts_manager.counter_max
        self.otp_progress_bar.set_fraction(counter_fraction)
        self.otp_progress_bar.set_tooltip_text(_("The One-Time Passwords expires in {} seconds").format(counter))


class ProviderWidget(Gtk.Box):

    def __init__(self, accounts_list, provider):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.provider = provider
        self._build_widgets(accounts_list, provider)

    def _build_widgets(self, accounts_list, provider):
        provider_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        provider_lbl = Gtk.Label()
        provider_lbl.set_text(provider)
        provider_lbl.set_halign(Gtk.Align.START)
        provider_lbl.get_style_context().add_class("provider-lbl")

        provider_img = Gtk.Image()
        pixbuf = load_pixbuf_from_provider(provider)
        provider_img.set_from_pixbuf(pixbuf)

        provider_container.pack_start(provider_img, False, False, 3)
        provider_container.pack_start(provider_lbl, False, False, 3)

        self.pack_start(provider_container, False, False, 3)
        self.pack_start(accounts_list, False, False, 3)


class AccountsListState:
    NORMAL = 0
    SELECT = 1


class AccountsList(Gtk.ListBox, GObject.GObject):
    """Accounts List."""

    __gsignals__ = {
        'selected-count-rows-changed': (GObject.SignalFlags.RUN_LAST, None, (int,)),
        'account-deleted': (GObject.SignalFlags.RUN_LAST, None, ()),
    }
    # Default instance of accounts list
    instance = None

    def __init__(self):
        GObject.GObject.__init__(self)
        Gtk.ListBox.__init__(self)
        self.set_selection_mode(Gtk.SelectionMode.NONE)
        self.get_style_context().add_class("accounts-list")
        self.state = AccountsListState.NORMAL
        self.selected_rows_count = 0

    def append_new(self, name, provider, token):
        account = Account.create(name, provider, token)
        self._add_row(account)

    def append(self, _id, name, provider, secret_id):
        account = Account(_id, name, provider, secret_id)
        self._add_row(account)

    def delete(self, _):
        # Remove an account from the list
        self.emit("changed", False)

    def set_state(self, state):
        show_check_btn = (state == AccountsListState.SELECT)
        for child in self.get_children():
            child.check_btn.set_visible(show_check_btn)
            child.check_btn.set_no_show_all(not show_check_btn)

    def delete_selected(self, *_):
        for child in self.get_children():
            check_btn = child.check_btn
            if check_btn.props.active:
                child.account.remove()
                self.remove(child)
        self.emit("account-deleted")
        self.set_state(AccountsListState.NORMAL)

    def _add_row(self, account):
        AccountsManager.get_default().add(account)
        row = AccountRow(account)
        row.connect("on_selected", self._on_row_checked)
        self.add(row)

    def _on_row_checked(self, _):
        self.selected_rows_count = 0
        for _row in self.get_children():
            if _row.check_btn.props.active:
                self.selected_rows_count += 1
        self.emit("selected-count-rows-changed", self.selected_rows_count)


class EmptyAccountsList(Gtk.Box):
    """
        Empty accounts list widget.
    """
    # Default instance
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
        """
            Build EmptyAccountList widget.
        """
        self.set_border_width(36)
        self.set_valign(Gtk.Align.CENTER)
        self.set_halign(Gtk.Align.CENTER)

        # Image
        g_icon = Gio.ThemedIcon(name="dialog-information-symbolic.symbolic")
        img = Gtk.Image.new_from_gicon(g_icon, Gtk.IconSize.DIALOG)

        # Label
        label = Gtk.Label(label=_("There are no accounts yet…"))

        self.pack_start(img, False, False, 6)
        self.pack_start(label, False, False, 6)
