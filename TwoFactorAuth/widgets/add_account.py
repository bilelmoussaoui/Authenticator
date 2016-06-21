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
from gi.repository import Gtk, Gdk, Gio
import logging
from TwoFactorAuth.utils import screenshot_area, current_date_time
from TwoFactorAuth.widgets.applications_list import ApplicationChooserWindow
from TwoFactorAuth.models.code import Code
from TwoFactorAuth.models.qr_reader import QRReader
from TwoFactorAuth.utils import get_icon
from gettext import gettext as _


class AddAccount(Gtk.Window):

    def __init__(self, window):
        self.parent = window

        self.selected_logo = None
        self.step = 1
        self.account_image = Gtk.Image(xalign=0)
        self.secret_code = Gtk.Entry()
        self.name_entry = Gtk.Entry()
        self.hb = Gtk.HeaderBar()

        self.generate_window()
        self.generate_components()
        self.generate_header_bar()

    def generate_window(self):
        Gtk.Window.__init__(self, type=Gtk.WindowType.TOPLEVEL, title=_("Add a new account"),
                            modal=True, destroy_with_parent=True)
        self.connect("delete-event", self.close_window)
        self.resize(420, 300)
        self.set_border_width(18)
        self.set_size_request(420, 300)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_resizable(False)
        self.set_transient_for(self.parent)
        self.connect("key_press_event", self.on_key_press)

    def generate_header_bar(self):
        """
            Generate the header bar box
        """
        self.hb.props.title = _("Add a new account")

        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        cancel_button = Gtk.Button.new_with_label(_("Cancel"))
        cancel_button.connect("clicked", self.close_window)
        cancel_button.get_style_context().add_class("destructive-action")
        left_box.add(cancel_button)

        self.apply_button = Gtk.Button.new_with_label(_("Add"))
        self.apply_button.get_style_context().add_class("suggested-action")
        self.apply_button.connect("clicked", self.add_account)
        self.apply_button.set_sensitive(False)

        qr_button = Gtk.Button()
        qr_icon = Gio.ThemedIcon(name="camera-photo-symbolic")
        qr_image = Gtk.Image.new_from_gicon(qr_icon, Gtk.IconSize.BUTTON)
        qr_button.set_tooltip_text(_("Scan a QR code"))
        qr_button.set_image(qr_image)
        qr_button.connect("clicked", self.on_qr_scan)

        right_box.add(qr_button)
        right_box.add(self.apply_button)

        self.hb.pack_start(left_box)
        self.hb.pack_end(right_box)
        self.set_titlebar(self.hb)

    def generate_components(self):
        """
            Generate window components
        """
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        labels_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        logo_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        hbox_name = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
        account_name = Gtk.Label()
        account_name.set_text(_("Account Name"))

        hbox_name.pack_end(self.name_entry, False, True, 0)
        hbox_name.pack_end(account_name, False, True, 0)

        hbox_secret_code = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
        secret_code_label = Gtk.Label()
        secret_code_label.set_text(_("Secret Code"))
        self.secret_code.connect("changed", self.validate_ascii_code)

        hbox_secret_code.pack_end(self.secret_code, False, True, 0)
        hbox_secret_code.pack_end(secret_code_label, False, True, 0)

        account_logo = get_icon("image-missing")
        self.account_image.set_from_pixbuf(account_logo)
        self.account_image.get_style_context().add_class("application-logo-add")
        logo_box.pack_start(self.account_image, True, False, 6)
        logo_box.set_property("margin-bottom", 20)

        vbox.add(hbox_name)
        vbox.add(hbox_secret_code)
        labels_box.pack_start(vbox, True, False, 6)
        main_box.pack_start(logo_box, False, True, 6)
        main_box.pack_start(labels_box, False, True, 6)
        self.add(main_box)

    def on_qr_scan(self, *args):
        filename = "/tmp/TwoFactorAuth-%s.png" % current_date_time()
        if screenshot_area(filename):
            qr = QRReader(filename)
            data = qr.read()
            if qr.is_valid():
                self.name_entry.set_text(data["issuer"])
                self.secret_code.set_text(data["secret"])
                self.apply_button.set_sensitive(True)

    def on_key_press(self, key, key_event):
        """
            Keyboard Listener handler
        """
        key_name = Gdk.keyval_name(key_event.keyval).lower()
        if key_name == "escape":
            self.close_window()
            return True

        if key_name == "return":
            if self.apply_button.get_sensitive():
                self.add_account()
                return True

        if key_event.state & Gdk.ModifierType.CONTROL_MASK:
            if key_name == 's':
                self.on_qr_scan()
                return True

        return False

    def update_logo(self, image):
        """
            Update image logo
        """
        self.selected_logo = image
        account_icon = get_icon(image)
        self.account_image.clear()
        self.account_image.set_from_pixbuf(account_icon)

    def validate_ascii_code(self, entry):
        """
            Validate if the typed secret code is a valid ascii one
        """
        ascii_code = entry.get_text().strip()
        is_valid = Code.is_valid(ascii_code)
        self.apply_button.set_sensitive(is_valid)
        if not is_valid and len(ascii_code) != 0:
            entry.set_icon_from_icon_name(
                Gtk.EntryIconPosition.SECONDARY, "dialog-error-symbolic")
        else:
            entry.set_icon_from_icon_name(
                Gtk.EntryIconPosition.SECONDARY, None)

    def add_account(self, *args):
        """
            Add a new application to the database
        """
        name = self.name_entry.get_text()
        secret_code = self.secret_code.get_text()
        logo = self.selected_logo if self.selected_logo else "image-missing"
        try:
            self.parent.app.db.add_account(name, secret_code, logo)
            uid = self.parent.app.db.get_latest_id()
            self.parent.accounts_list.append([uid, name, secret_code, logo])
            self.parent.refresh_window()
            self.close_window()
        except Exception as e:
            logging.error("Error in adding a new account")
            logging.error(str(e))

    def show_window(self):
        if self.step == 1:
            applications_choose_window = ApplicationChooserWindow(self)
            applications_choose_window.show_window()
            applications_choose_window.present()
            self.step = 2
        else:
            self.name_entry.grab_focus_without_selecting()
            self.show_all()

    def close_window(self, *args):
        """
            Close the window
        """
        self.destroy()
