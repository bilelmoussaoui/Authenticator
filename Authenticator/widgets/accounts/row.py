"""
 Copyright © 2017 Bilal Elmoussaoui <bil.elmoussaoui@gmail.com>

 This file is part of Gnome Authenticator.

 Gnome Authenticator is free software: you can redistribute it and/or
 modify it under the terms of the GNU General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 TwoFactorAuth is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Gnome Authenticator. If not, see <http://www.gnu.org/licenses/>.
"""
from gettext import gettext as _

from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk


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
        self.edit_btn = ActionButton("document-edit-symbolic", _("Edit"))
        self.apply_btn = ActionButton("emblem-ok-symbolic", _("Apply"))
        self._build_widget()

    def _build_widget(self):
        """Build ActionsBox widgets."""
        self.pack_start(self.copy_btn, False, False, 0)
        self.pack_start(self.edit_btn, False, False, 0)
        self.pack_start(self.apply_btn, False, False, 0)
        # Hide the apply btn by default
        self.apply_btn.hide()


class AccountRow(Gtk.ListBoxRow):
    """Account Row widget."""

    def __init__(self, account):
        Gtk.ListBoxRow.__init__(self)
        self.get_style_context().add_class("application-list-row")
        self._account = account
        self._account.connect("code_updated", self._on_code_updated)
        self._account.connect("name_updated", self._on_name_updated)
        self._account.connect("counter_updated", self._on_counter_updated)
        self._build_widget()

    @property
    def account(self):
        return self._account

    def _build_widget(self):
        """Build the Account Row widget."""
        container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                            spacing=6)

        # Account Image
        theme = Gtk.IconTheme.get_default()
        if theme.has_icon(self.account.logo):
            icon_name = self.account.logo
        else:
            # TODO: replace this icon name with something else
            icon_name = "image-missing"
        image = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DIALOG)
        container.pack_start(image, False, False, 6)

        # Account Name & Two factor code:
        info_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # Account Name
        self.name_lbl = Gtk.Label(self.account.name)
        self.name_lbl.set_halign(Gtk.Align.START)
        self.name_lbl.get_style_context().add_class("application-name")

        # Two Factor Code
        self._code_revealer = Gtk.Revealer()
        code_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        secret_code = self.account.secret_code    
        self.code_lbl = Gtk.Label()
        if secret_code:
            self.code_lbl.set_text(secret_code)
        else:
            self.code_lbl.set_text(_("Couldn't generate the secret code"))
        self.code_lbl.set_halign(Gtk.Align.START)
        
        # Counter
        self.counter_lbl = Gtk.Label()
        if secret_code:
            self.update_counter()
        else:
            self.counter_lbl.set_text("")
        code_container.pack_start(self.code_lbl, False, False, 0)
        code_container.pack_end(self.counter_lbl, False, False, 0)
        self._code_revealer.add(code_container)

        info_container.pack_start(self.name_lbl, False, False, 0)
        info_container.pack_start(self._code_revealer, True, True, 0)
        container.pack_start(info_container, True, True, 6)

        # Actions container
        actions = ActionsBox()
        container.pack_end(actions, False, False, 6)


        self.add(container)

    def toggle_secret_code(self):
        is_visible = self._code_revealer.get_reveal_child()
        self._code_revealer.set_reveal_child(not is_visible) 

    def update_counter(self):
        counter = self.account.counter    
        self.counter_lbl.set_text("Expires in {} seconds".format(counter))

    def _on_code_updated(self, *args):
        print(args)

    def _on_name_updated(self, *args):
        print(args)

    def _on_counter_updated(self, *args):
        self.update_counter()