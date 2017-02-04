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

import logging
import yaml
from glob import glob
from threading import Thread
from os import path, environ as env
from Authenticator.utils import screenshot_area
from Authenticator.widgets.inapp_notification import InAppNotification
from Authenticator.widgets.search_bar import SearchBar
from Authenticator.models.code import Code
from Authenticator.models.qr_reader import QRReader
from Authenticator.utils import get_icon
from gettext import gettext as _
from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject, Gio, Gdk, GLib
""" TODO :
add back button
rewrite the ui using Glade and Builder
"""


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
        Gtk.Window.__init__(self, type=Gtk.WindowType.TOPLEVEL,
                            title=_("Add a new account"),
                            modal=True, destroy_with_parent=True)
        self.connect("delete-event", self.close_window)
        self.resize(500, 350)
        self.set_size_request(500, 350)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_resizable(False)
        self.set_transient_for(self.parent)
        self.notification = InAppNotification()

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
        qr_icon = Gio.ThemedIcon(name="qrscanner-symbolic")
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
        logo_box.props.margin_top = 18

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

        account_logo = get_icon("image-missing", 48)
        self.account_image.set_from_pixbuf(account_logo)
        self.account_image.get_style_context().add_class("application-logo-add")
        logo_box.pack_start(self.account_image, True, False, 6)
        logo_box.set_property("margin-bottom", 20)

        vbox.add(hbox_name)
        vbox.add(hbox_secret_code)
        labels_box.pack_start(vbox, True, False, 6)
        main_box.pack_start(self.notification, False, False, 0)
        main_box.pack_start(logo_box, False, True, 6)
        main_box.pack_start(labels_box, False, True, 6)
        self.add(main_box)

    def on_qr_scan(self, *args):
        filename = screenshot_area()
        if filename:
            qr = QRReader(filename)
            data = qr.read()
            if qr.is_valid():
                self.name_entry.set_text(data["issuer"])
                self.secret_code.set_text(data["secret"])
                self.apply_button.set_sensitive(True)
            else:
                self.notification.set_message(
                    _("Selected area is not a valid QR code"))
                self.notification.set_message_type(Gtk.MessageType.ERROR)
                self.notification.show()

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
        account_icon = get_icon(image, 48)
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
            new_account = self.parent.app.db.add_account(
                name, secret_code, logo)
            self.parent.accounts_box.append(new_account)
            self.close_window()
        except Exception as e:
            logging.error("Error in addin.accounts_boxg a new account")
            logging.error(str(e))

    def show_window(self):
        if self.step == 1:
            applications_choose_window = ApplicationChooserWindow(self, self.parent)
            applications_choose_window.show_window()
            self.step = 2
        else:
            self.secret_code.grab_focus_without_selecting()
            self.show_all()

    def close_window(self, *args):
        """
            Close the window
        """
        self.destroy()

class ApplicationRow(Gtk.ListBoxRow):

    def __init__(self, name, image):
        Gtk.ListBoxRow.__init__(self)
        self.name = name
        self.image = image
        # Create the list row
        self.create_row()

    def get_name(self):
        """
            Get the application label
            :return: (str): application label
        """
        return self.name

    def get_icon_name(self):
        return self.image

    def get_icon(self):
        return get_icon(self.image, 48)

    def create_row(self):
        """
            Create ListBoxRow
        """
        self.builder = Gtk.Builder.new_from_resource("/org/gnome/Authenticator/application_row.ui")
        self.builder.get_object("ApplicationLogo").set_from_pixbuf(self.get_icon())
        self.builder.get_object("ApplicationName").set_text(self.name)
        self.add(self.builder.get_object("MainBox"))


class ApplicationChooserWindow(Thread, GObject.GObject):
    __gsignals__ = {
        'db_updated': (GObject.SignalFlags.RUN_LAST, None, (bool,))
    }

    def __init__(self, parent, main_window):
        self.parent = parent
        Thread.__init__(self)
        GObject.GObject.__init__(self)
        self.nom = "applications-db-reader"
        self.builder = Gtk.Builder.new_from_resource("/org/gnome/Authenticator/applications.ui")
        self.builder.connect_signals({
            "on_close" : self.close_window,
            "on_key_press": self.on_key_press,
            "on_apply" : self.select_application
        })
        self.window = self.builder.get_object("ApplicationsWindow")
        self.window.set_transient_for(main_window)
        self.listbox = self.builder.get_object("ApplicationsList")
        self.generate_search_bar()
        self.stack = self.builder.get_object("ApplicationsStack")
        self.stack.set_visible_child(self.stack.get_child_by_name("loadingstack"))
        self.builder.get_object("ApplicationListScrolled").add_with_viewport(self.listbox)
        self.db = []
        self.start()

    def emit(self, *args):
        GLib.idle_add(GObject.GObject.emit, self, *args)

    def run(self):
        # Load applications list using a Thread
        self.builder.get_object("LoadingSpinner").start()
        self.read_database()
        self.add_apps()
        self.emit("db_updated", True)

    def generate_search_bar(self):
        """Generate the search bar."""
        search_button = self.builder.get_object("SearchButton")
        main_box = self.builder.get_object("MainBox")
        self.search_bar = SearchBar(self.window, search_button, [self.listbox])
        main_box.pack_start(self.search_bar, False, True, 0)
        main_box.reorder_child(self.search_bar, 0)


    def is_valid_app(self, app):
        """
            Check if the application supports tfa
        """
        if set(["tfa", "software"]).issubset(app.keys()):
            return app["tfa"] and app["software"]
        else:
            return False

    def on_key_press(self, label, key_event):
        """
            Keyboard listener handling
        """
        keyname = Gdk.keyval_name(key_event.keyval).lower()

        if keyname == "escape":
            if not self.search_bar.is_visible():
                self.close_window()
                return True

        if keyname == "up" or keyname == "down":
            dx = -1 if keyname == "up" else 1
            index = self.listbox.get_selected_row().get_index()
            index = (index + dx) % len(self.db)
            selected_row = self.listbox.get_row_at_index(index)
            self.listbox.select_row(selected_row)
            return True

        if keyname == "return":
            self.select_application()
            return True
        return False

    def do_db_updated(self, *args):
        """
            Hide and stop the spinner and show the scrolled window
        """
        self.builder.get_object("LoadingSpinner").stop()
        self.stack.set_visible_child(self.stack.get_child_by_name("applicationsliststack"))
        self.listbox.show_all()
        logging.debug("UI updated")

    def read_database(self):
        """
            Read .yml database files provided by 2factorauth guys!
        """
        db_dir = path.join(env.get("DATA_DIR"), "applications") + "/data/*.yml"
        logging.debug("Database folder is {0}".format(db_dir))
        db_files = glob(db_dir)
        logging.debug("Reading database files started")
        for db_file in db_files:
            logging.debug("Reading database file {0}".format(db_file))
            with open(db_file, 'r') as data:
                try:
                    websites = yaml.load(data)["websites"]
                    for app in websites:
                        if self.is_valid_app(app):
                            self.db.append(app)
                except yaml.YAMLError as error:
                    logging.error("Error loading yml file {0} : {1}".format(
                        db_file, str(error)))
                except TypeError:
                    logging.error("Not a valid yml file {0}".format(db_file))
        logging.debug("Reading database files finished")

    def add_apps(self):
        """
            Add database applications to the Gtk.ListBox
        """
        self.db = sorted(self.db, key=lambda k: k['name'].lower())
        logging.debug("Application list was ordered alphabetically")

        for app in self.db:
            img_path = app["img"]
            app_name = app["name"]
            self.listbox.add(ApplicationRow(app_name, img_path))

        if len(self.db) != 0:
            self.listbox.select_row(self.listbox.get_row_at_index(0))

    def select_application(self, *args):
        """
            Select a logo and return its path to the add application window
        """
        selected_row = self.listbox.get_selected_row()
        if selected_row:
            img_path = selected_row.get_icon_name()
            app_name = selected_row.get_name()
            logging.debug("%s was selected" % app_name)
            self.parent.update_logo(img_path)
            self.parent.name_entry.set_text(app_name)
            self.parent.show_window()
            self.parent.present()
            self.close_window()

    def show_window(self):
        self.window.show_all()
        self.window.present()

    def close_window(self, *args):
        """
            Close the window
        """
        logging.debug("Closing ApplicationChooserWindow")
        self.window.destroy()
