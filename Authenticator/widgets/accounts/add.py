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
import json
from gettext import gettext as _

from gi import require_version

require_version("Gtk", "3.0")
require_version('Gd', '1.0')

from gi.repository import Gd, Gio, Gtk, GObject, Gdk

from ..headerbar import HeaderBarButton
from ...models import OTP
from ...utils import can_use_qrscanner, load_pixbuf_from_provider


class AddAccountWindow(Gtk.Window):
    """Add Account Window."""

    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_size_request(400, 600)
        self.resize(400, 600)
        self._build_widgets()
        self.connect('key_press_event', self._on_key_press)

    def _build_widgets(self):
        """Create the Add Account widgets."""
        # Header Bar
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_close_button(False)
        header_bar.set_title(_("Add a new account"))
        self.set_titlebar(header_bar)
        # Next btn
        self.add_btn = Gtk.Button()
        self.add_btn.set_label(_("Add"))
        self.add_btn.connect("clicked", self._on_add)
        self.add_btn.get_style_context().add_class("suggested-action")
        self.add_btn.set_sensitive(False)
        header_bar.pack_end(self.add_btn)

        # QR code scan btn
        from ...application import Application
        self.scan_btn = HeaderBarButton("qrscanner-symbolic",
                                        _("Scan QR code"))
        if Application.USE_QRSCANNER and can_use_qrscanner():
            self.scan_btn.connect("clicked", self._on_scan)
            header_bar.pack_end(self.scan_btn)

        # Back btn
        self.close_btn = Gtk.Button()
        self.close_btn.set_label(_("Close"))
        self.close_btn.connect("clicked", self._on_quit)

        header_bar.pack_start(self.close_btn)

        self.account_config = AccountConfig()
        self.account_config.connect("changed", self._on_account_config_changed)

        self.add(self.account_config)

    def _on_scan(self, *_):
        """
            QR Scan button clicked signal handler.
        """
        if self.account_config:
            self.account_config.scan_qr()

    def _on_account_config_changed(self, _, state):
        """Set the sensitivity of the AddButton depends on the AccountConfig."""
        self.add_btn.set_sensitive(state)

    def _on_quit(self, *_):
        self.destroy()

    def _on_add(self, *_):
        from .list import AccountsWidget
        from ...models import AccountsManager, Account
        account_obj = self.account_config.account
        account = Account.create(account_obj["username"], account_obj["provider"], account_obj["token"])
        AccountsManager.get_default().add(account)
        AccountsWidget.get_default().append(account)
        self._on_quit()

    def _on_key_press(self, _, event):
        _, key_val = event.get_keyval()
        modifiers = event.get_state()

        if key_val == Gdk.KEY_Escape:
            self._on_quit()

        # CTRL + Q
        if modifiers == Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.MOD2_MASK:
            if key_val == Gdk.KEY_q:
                self._on_scan()


class AccountConfig(Gtk.Box, GObject.GObject):
    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_LAST, None, (bool,)),
    }

    def __init__(self, **kwargs):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        GObject.GObject.__init__(self)

        self.is_edit = kwargs.get("edit", False)
        self._account = kwargs.get("account", None)

        self._providers_store = Gtk.ListStore(str, str)

        self.logo_img = Gtk.Image()
        self.username_entry = Gtk.Entry()
        self.provider_combo = Gtk.ComboBox.new_with_model_and_entry(
            self._providers_store)
        self.token_entry = Gtk.Entry()
        self._build_widgets()
        self._fill_data()

    @property
    def account(self):
        """
            Return an instance of Account for the new account.
        """
        account = {
            "username": self.username_entry.get_text(),
            "provider": self.provider_combo.get_child().get_text()
        }

        if not self.is_edit:
            account["token"] = self.token_entry.get_text()
        return account

    def _build_widgets(self):

        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        container.set_border_width(36)

        self.provider_combo.set_entry_text_column(0)
        self.provider_combo.connect("changed", self._on_provider_changed)
        # Set up auto completion
        provider_entry = self.provider_combo.get_child()
        provider_entry.set_placeholder_text(_("Provider"))

        completion = Gtk.EntryCompletion()
        completion.set_model(self._providers_store)
        completion.set_text_column(0)

        provider_entry.set_completion(completion)
        if self._account:
            provider_entry.set_text(self._account.provider)

        self.username_entry.set_placeholder_text(_("Account name"))
        self.username_entry.connect("changed", self._validate)
        if self._account:
            self.username_entry.set_text(self._account.username)

        if not self.is_edit:
            self.token_entry.set_placeholder_text(_("Secret token"))
            self.token_entry.set_visibility(False)
            self.token_entry.connect("changed", self._validate)

        # To set the empty logo

        if self._account:
            pixbuf = load_pixbuf_from_provider(self._account.provider, 96)
        else:
            pixbuf = load_pixbuf_from_provider(None, 96)

        self.logo_img.set_from_pixbuf(pixbuf)

        container.pack_start(self.logo_img, False, False, 6)
        if not self.is_edit:
            container.pack_end(self.token_entry, False, False, 6)
        container.pack_end(self.username_entry, False, False, 6)
        container.pack_end(self.provider_combo, False, False, 6)

        self.pack_start(container, False, False, 6)

    def _on_provider_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            logo = model[tree_iter][-1]
        else:
            entry = combo.get_child()
            logo = entry.get_text()
        self._validate()
        self.logo_img.set_from_pixbuf(load_pixbuf_from_provider(logo, 96))

    def _fill_data(self):
        uri = 'resource:///com/github/bilelmoussaoui/Authenticator/data.json'
        g_file = Gio.File.new_for_uri(uri)
        content = str(g_file.load_contents(None)[1].decode("utf-8"))
        data = json.loads(content)
        data = sorted([(name, logo) for name, logo in data.items()],
                      key=lambda account: account[0].lower())
        for entry in data:
            name, logo = entry
            self._providers_store.append([name, logo])

    def _validate(self, *_):
        """Validate the username and the token."""
        provider = self.provider_combo.get_child().get_text()
        username = self.username_entry.get_text()
        token = self.token_entry.get_text()

        if not username:
            self.username_entry.get_style_context().add_class("error")
            valid_name = False
        else:
            self.username_entry.get_style_context().remove_class("error")
            valid_name = True

        if not provider:
            self.provider_combo.get_style_context().add_class("error")
            valid_provider = False
        else:
            self.provider_combo.get_style_context().remove_class("error")
            valid_provider = True

        if (not token or not OTP.is_valid(token)) and not self.is_edit:
            self.token_entry.get_style_context().add_class("error")
            valid_token = False
        else:
            self.token_entry.get_style_context().remove_class("error")
            valid_token = True

        self.emit("changed", all([valid_name, valid_provider, valid_token]))

    def scan_qr(self):
        """
            Scans a QRCode and fills the entries with the correct data.
        """
        from ...models import QRReader, GNOMEScreenshot
        filename = GNOMEScreenshot.area()
        if filename:
            qr_reader = QRReader(filename)
            secret = qr_reader.read()
            if not qr_reader.is_valid():
                self.__send_notification(_("Invalid QR code"))
            else:
                self.token_entry.set_text(secret)

    def __send_notification(self, message):
        """
            Show a notification using Gd.Notification.
            :param message: the notification message
            :type message: str
        """
        notification = Gd.Notification()
        notification.set_show_close_button(True)
        notification.set_timeout(5)

        notification_lbl = Gtk.Label()
        notification_lbl.set_text(message)

        notification.add(notification_lbl)

        self.add(notification)
        self.reorder_child(notification, 0)
        self.show_all()
