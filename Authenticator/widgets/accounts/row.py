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
from gi.repository import Gio, Gtk, GObject, GLib, Pango

from ..password_label import PasswordLabel


class ActionButton(Gtk.Button):

    def __init__(self, icon_name, tooltip):
        Gtk.Button.__init__(self)
        self.get_style_context().add_class("flat")
        self._build_widget(icon_name, tooltip)

    def _build_widget(self, icon_name, tooltip):
        icon = Gio.ThemedIcon(name=icon_name)
        image = Gtk.Image.new_from_gicon(icon,
                                         Gtk.IconSize.BUTTON)
        self.set_tooltip_text(tooltip)
        self.set_image(image)

    def hide(self):
        self.set_visible(False)
        self.set_no_show_all(True)

    def show(self):
        self.set_visible(True)
        self.set_no_show_all(False)


class ActionsBox(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        self.copy_btn = ActionButton("edit-copy-symbolic", _("Copy"))
        self._build_widget()

    def _build_widget(self):
        """Build ActionsBox widgets."""
        self.pack_start(self.copy_btn, False, False, 0)


class AccountRow(Gtk.ListBoxRow, GObject.GObject):
    """Accounts List."""

    __gsignals__ = {
        'on_selected': (GObject.SignalFlags.RUN_LAST, None, ()),
    }

    def __init__(self, account):
        Gtk.ListBoxRow.__init__(self)
        self.get_style_context().add_class("application-list-row")
        self._account = account
        self.check_btn = Gtk.CheckButton()
        self.counter_lbl = Gtk.Label()
        self._account.connect("code_updated", self._on_code_updated)
        self._account.connect("counter_updated", self._on_counter_updated)
        self._build_widget()
        self.show_all()

    @property
    def account(self):
        return self._account

    @property
    def checked(self):
        return self.check_btn.get_active()

    def get_name(self):
        """
            Required by SearchBar
        """
        return self._account.name

    def _build_widget(self):
        """Build the Account Row widget."""
        container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                            spacing=6)

        container.pack_start(self.check_btn, False, False, 3)
        self.check_btn.set_visible(False)
        self.check_btn.connect("toggled", self._on_toggled)
        self.check_btn.set_no_show_all(True)

        # Account Image
        theme = Gtk.IconTheme.get_default()
        try:
            pixbuf = theme.load_icon(self.account.logo, 48, 0)
            image = Gtk.Image.new_from_pixbuf(pixbuf)
        except GLib.Error:
            image = Gtk.Image.new_from_icon_name(
                "com.github.bilelmoussaoui.Authenticator", Gtk.IconSize.DIALOG)

        container.pack_start(image, False, False, 6)

        # Account Name & Two factor code:
        info_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Service Provider
        self.provider_lbl = Gtk.Label(label=self.account.provider)
        self.provider_lbl.set_halign(Gtk.Align.START)
        self.provider_lbl.get_style_context().add_class("provider-lbl")

        # Account Name
        self.name_lbl = Gtk.Label(label=self.account.name)
        self.name_lbl.set_tooltip_text(self.account.name)
        self.name_lbl.set_ellipsize(Pango.EllipsizeMode.END)
        self.name_lbl.set_halign(Gtk.Align.START)
        self.name_lbl.get_style_context().add_class("application-name")

        info_container.pack_start(self.provider_lbl, False, False, 0)
        info_container.pack_start(self.name_lbl, False, False, 0)
        info_container.set_valign(Gtk.Align.CENTER)
        container.pack_start(info_container, True, True, 6)

        # Actions container
        actions = ActionsBox()
        actions.copy_btn.connect("clicked", self._on_copy)
        actions.set_valign(Gtk.Align.CENTER)
        container.pack_end(actions, False, False, 6)

        # Secret code
        code_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        secret_code = self.account.secret_code
        self.code_lbl = PasswordLabel()
        self.code_lbl.set_halign(Gtk.Align.START)
        self.code_lbl.get_style_context().add_class("flat")
        if secret_code:
            self.code_lbl.text = secret_code
        else:
            self.code_lbl.text = _("Couldn't generate the secret code")
        self.code_lbl.get_style_context().add_class("token-label")
        self.code_lbl.set_visibility(False)
        # Counter
        if secret_code:
            self.update_counter()
        else:
            self.counter_lbl.set_text("")
        self.counter_lbl.get_style_context().add_class("counter-label")
        self.counter_lbl.set_ellipsize(Pango.EllipsizeMode.END)

        code_container.pack_start(self.code_lbl, True, True, 6)
        code_container.pack_end(self.counter_lbl, True, True, 6)
        code_container.set_valign(Gtk.Align.CENTER)
        container.pack_end(code_container, False, False, 6)

        self.add(container)

    def _toggle_secret_code(self, *args):
        self.code_lbl.set_visibility(not self.code_lbl.get_visibility())

    def _on_toggled(self, *args):
        self.emit("on_selected")

    def _on_copy(self, *args):
        self._account.copy_token()

    def update_counter(self):
        counter = self.account.counter
        text = "Expires in {} seconds".format(counter)
        self.counter_lbl.set_text(text)
        self.counter_lbl.set_tooltip_text(text)

    def _on_code_updated(self, account, code):
        self.code_lbl.text = code

    def _on_counter_updated(self, *args):
        if self.account.secret_code:
            self.update_counter()
