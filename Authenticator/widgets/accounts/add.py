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
import json

from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk, GObject, GLib

from ..headerbar import HeaderBarButton, HeaderBarToggleButton
from ..inapp_notification import InAppNotification
from ..search_bar import SearchBar
from ...models import Code
from ...utils import can_use_qrscanner


class AddAcountWindow(Gtk.Window):
    """Add Account Window."""
    STEP = 1

    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_size_request(400, 600)
        self.resize(400, 600)
        self._signals = {}
        self._build_widgets()

    def _build_widgets(self):
        """Create the Add Account widgets."""
        # Header Bar
        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(False)
        headerbar.set_title(_("Add a new account"))
        self.set_titlebar(headerbar)
        # Next btn
        self.next_btn = Gtk.Button()
        self.next_btn.get_style_context().add_class("suggested-action")
        headerbar.pack_end(self.next_btn)

        # Search btn
        self.search_btn = HeaderBarToggleButton("system-search-symbolic",
                                                _("Search"))
        headerbar.pack_end(self.search_btn)
        # QR code scan btn
        from ...application import Application
        self.scan_btn = HeaderBarButton("qrscanner-symbolic",
                                        _("Scan QR code"))
        if Application.USE_QRSCANNER and can_use_qrscanner():
            self.scan_btn.connect("clicked", self._on_scan)
            headerbar.pack_end(self.scan_btn)

        # Back btn
        self.back_btn = Gtk.Button()

        headerbar.pack_start(self.back_btn)

        # Main stack
        self.main = Gtk.Stack()
        self.accounts_list = AccountsList()
        self.accounts_list.search_bar.search_button = self.search_btn
        # Create a scrollted window for the accounts list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER,
                            Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.accounts_list)
        self.main.add_named(scrolled, "1")
        self.account_config = AccountConfig()
        self.account_config.connect("changed", self._on_account_config_changed)
        self.main.add_named(self.account_config, "2")

        self.add(self.main)
        # The first step!
        self._set_step(1)

    def _set_step(self, step):
        AddAcountWindow.STEP = step
        search_btn_visible = False
        scan_btn_visible = False
        if self._signals:
            self.back_btn.disconnect(self._signals["back"])
            self.next_btn.disconnect(self._signals["next"])
        if step == 1:
            next_lbl = _("Next")
            back_lbl = _("Close")
            search_btn_visible = True
            self.next_btn.set_sensitive(True)
            self._signals["back"] = self.back_btn.connect("clicked",
                                                          self._on_quit)
            self._signals["next"] = self.next_btn.connect("clicked",
                                                          lambda x: self._set_step(2))
        elif step == 2:
            next_lbl = _("Add")
            back_lbl = _("Back")
            scan_btn_visible = True
            account = self.accounts_list.get_selected_row()
            self.account_config.set_account(account)
            self.account_config.name_entry.emit("changed")
            self.next_btn.set_sensitive(False)
            self._signals["back"] = self.back_btn.connect("clicked",
                                                          lambda x: self._set_step(1))
            self._signals["next"] = self.next_btn.connect("clicked",
                                                          self._on_add)
        self.next_btn.set_label(next_lbl)
        self.back_btn.set_label(back_lbl)

        self.scan_btn.set_visible(scan_btn_visible)
        self.scan_btn.set_no_show_all(not scan_btn_visible)

        self.search_btn.set_visible(search_btn_visible)
        self.search_btn.set_no_show_all(not search_btn_visible)

        self.main.set_visible_child_name(str(step))

    def _on_scan(self, widget):
        """
            QR Scan button clicked signal handler.
        """
        if self.account_config:
            self.account_config.scan_qr()

    def _on_account_config_changed(self, widget, state):
        self.next_btn.set_sensitive(state)

    def _on_quit(self, *args):
        self.destroy()

    def _on_add(self, *args):
        from .list import AccountsList
        name, provider, secret, logo = self.account_config.account.values()
        AccountsList.get_default().append(name, provider, secret, logo)
        self.destroy()


class AccountsList(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self._listbox = Gtk.ListBox()
        self.search_bar = SearchBar()
        self._build_widgets()
        self._fill_data()

    def _build_widgets(self):
        """
        Create the Accounts List widgets.
        """

        self.pack_start(self.search_bar, False, False, 0)
        self.search_bar.search_list = [self._listbox]
        self._listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)

        accounts_scrolled = Gtk.ScrolledWindow()
        accounts_scrolled.add_with_viewport(self._listbox)
        self.pack_start(accounts_scrolled, True, True, 0)

    def get_selected_row(self):
        return self._listbox.get_selected_row()

    def _fill_data(self):
        uri = 'resource:///com/github/bilelmoussaoui/Authenticator/data.json'
        file = Gio.File.new_for_uri(uri)
        content = str(file.load_contents(None)[1].decode("utf-8"))
        data = json.loads(content)
        data = sorted([(name, logo) for name, logo in data.items()],
                      key=lambda entry: entry[0].lower())
        for entry in data:
            name, logo = entry
            self._listbox.add(AccountRow(name, logo))


class AccountRow(Gtk.ListBoxRow):

    def __init__(self, name, logo):
        Gtk.ListBoxRow.__init__(self)
        self.name = name
        self.logo = logo
        self._build_widgets()

    def get_name(self):
        """Used by SearchBar."""
        return self.name

    def _build_widgets(self):
        container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        theme = Gtk.IconTheme.get_default()
        try:
            pixbuf = theme.load_icon(self.logo, 48, 0)
            logo_img = Gtk.Image.new_from_pixbuf(pixbuf)
        except GLib.Error:
            logo_img = Gtk.Image.new_from_icon_name(
                "com.github.bilelmoussaoui.Authenticator", Gtk.IconSize.DIALOG)

        container.pack_start(logo_img, False, False, 6)

        name_lbl = Gtk.Label(label=self.name)
        name_lbl.get_style_context().add_class("account-name")
        name_lbl.set_halign(Gtk.Align.START)
        container.pack_start(name_lbl, False, False, 6)
        self.add(container)


class AccountConfig(Gtk.Box, GObject.GObject):
    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_LAST, None, (bool,)),
    }

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        GObject.GObject.__init__(self)

        self.notification = InAppNotification()
        self.logo_img = Gtk.Image()
        self.name_entry = Gtk.Entry()
        self.provider_entry = Gtk.Entry()
        self.secret_entry = Gtk.Entry()
        self._logo = None
        self._build_widgets()

    @property
    def account(self):
        """
            Return an instance of Account for the new account.
        """
        account_name = self.name_entry.get_text()
        provider = self.provider_entry.get_text()
        secret = self.secret_entry.get_text()

        return {"name": account_name,
                "provider": provider,
                "secret": secret,
                "logo": self._logo}

    def _build_widgets(self):
        self.pack_start(self.notification, False, False, 0)

        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        container.set_border_width(18)

        self.provider_entry.set_sensitive(False)

        self.name_entry.set_placeholder_text(_("Account name"))
        self.name_entry.connect("changed", self._validate)
        self.secret_entry.set_placeholder_text(_("Secret Token"))
        self.secret_entry.connect("changed", self._validate)

        container.pack_start(self.logo_img, False, False, 6)
        container.pack_end(self.secret_entry, False, False, 6)
        container.pack_end(self.name_entry, False, False, 6)
        container.pack_end(self.provider_entry, False, False, 6)

        self.pack_start(container, False, False, 6)

    def _validate(self, *args):
        name = self.name_entry.get_text()
        secret_id = self.secret_entry.get_text()

        if not name:
            self.name_entry.get_style_context().add_class("error")
            valid_name = False
        else:
            self.name_entry.get_style_context().remove_class("error")
            valid_name = True
        if not Code.is_valid(secret_id):
            self.secret_entry.get_style_context().add_class("error")
            valid_secret = False
        else:
            self.secret_entry.get_style_context().remove_class("error")
            valid_secret = True
        self.emit("changed", valid_secret and valid_name)

    def set_account(self, account):
        name = account.name
        self._logo = account.logo

        self.provider_entry.set_text(name)
        theme = Gtk.IconTheme.get_default()
        try:
            pixbuf = theme.load_icon(self._logo, 48, 0)
            self.logo_img.set_from_pixbuf(pixbuf)
        except GLib.Error:
            self.logo_img.set_from_icon_name("com.github.bilelmoussaoui.Authenticator",
                                             Gtk.IconSize.DIALOG)

    def scan_qr(self):
        from ...models import QRReader, GNOMEScreenshot
        filename = GNOMEScreenshot.area()
        if filename:
            qr_reader = QRReader(filename)
            secret = qr_reader.read()
            if not qr_reader.is_valid():
                self.notification.set_message(_("Invalid QR code"))
                self.notification.set_message_type(Gtk.MessageType.ERROR)
                self.notification.show()
            else:
                self.secret_entry.set_text(secret)
