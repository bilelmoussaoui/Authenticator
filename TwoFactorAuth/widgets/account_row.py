from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject, GLib
from TwoFactorAuth.models.code import Code
from TwoFactorAuth.models.settings import SettingsReader
from TwoFactorAuth.models.database import Database
from TwoFactorAuth.utils import get_icon
from threading import Thread
from time import sleep
import logging
from gettext import gettext as _


class AccountRow(Thread, Gtk.ListBoxRow):
    counter_max = 30
    counter = 30
    timer = 0
    code = None
    code_generated = True
    alive = True

    def __init__(self, parent, uid, name, secret_code, logo):
        Thread.__init__(self)
        Gtk.ListBoxRow.__init__(self)
        # Read default values
        cfg = SettingsReader()
        self.counter_max = cfg.read("refresh-time", "preferences")
        self.counter = self.counter_max
        self.parent = parent
        self.id = uid
        self.name = name
        self.secret_code = Database.fetch_secret_code(secret_code)
        if self.secret_code:
            self.code = Code(self.secret_code)
        else:
            self.code_generated = False
            logging.error(
                "Could not read the secret code from, the keyring keys were reset manually")
        self.logo = logo
        # Create needed widgets
        self.code_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.revealer = Gtk.Revealer()
        self.checkbox = Gtk.CheckButton()
        self.application_name = Gtk.Label(xalign=0)
        self.code_label = Gtk.Label(xalign=0)
        self.timer_label = Gtk.Label(xalign=0)
        # Create the list row
        self.create_row()
        self.start()
        GLib.timeout_add_seconds(1, self.refresh_listbox)

    def get_id(self):
        """
            Get the application id
            :return: (int): row id
        """
        return self.id

    def get_name(self):
        """
            Get the application name
            :return: (str): application name
        """
        return self.name

    def get_code(self):
        return self.code

    def get_code_label(self):
        return self.code_label

    def get_checkbox(self):
        """
            Get ListBowRow's checkbox
            :return: (Gtk.Checkbox)
        """
        return self.checkbox

    def get_code_box(self):
        """
            Get code's box
            :return: (Gtk.Box)
        """
        return self.code_box

    def toggle_code_box(self):
        """
            Toggle code box
        """
        self.revealer.set_reveal_child(not self.revealer.get_reveal_child())

    def kill(self):
        """
            Kill the row thread once it's removed
        """
        self.alive = False

    def copy_code(self, event_box, box):
        """
            Copy code shows the code box for a while (10s by default)
        """
        self.timer = 0
        self.parent.copy_code(event_box)
        self.code_box.set_visible(True)
        self.code_box.set_no_show_all(False)
        self.code_box.show_all()
        GObject.timeout_add_seconds(1, self.update_timer)

    def update_timer(self, *args):
        """
            Update timer
        """
        self.timer += 1
        if self.timer > 10:
            self.code_box.set_visible(False)
            self.code_box.set_no_show_all(True)
        return self.timer <= 10

    def create_row(self):
        """
            Create ListBoxRow
        """
        self.get_style_context().add_class("application-list-row")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.pack_start(h_box, True, True, 0)
        box.pack_start(self.revealer, True, True, 0)

        # Checkbox
        self.checkbox.set_visible(False)
        self.checkbox.set_no_show_all(True)
        self.checkbox.connect("toggled", self.parent.select_account)
        h_box.pack_start(self.checkbox, False, True, 0)

        # account logo
        auth_icon = get_icon(self.logo)
        auth_logo = Gtk.Image(xalign=0)
        auth_logo.set_from_pixbuf(auth_icon)
        h_box.pack_start(auth_logo, False, True, 6)

        # accout name
        name_event = Gtk.EventBox()
        self.application_name .get_style_context().add_class("application-name")
        self.application_name .set_text(self.name)
        name_event.connect("button-press-event", self.toggle_code)
        name_event.add(self.application_name)
        h_box.pack_start(name_event, True, True, 6)
        # Copy button
        copy_event = Gtk.EventBox()
        copy_button = Gtk.Image(xalign=0)
        copy_button.set_from_icon_name(
            "edit-copy-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        copy_button.set_tooltip_text(_("Copy the generated code"))
        copy_event.connect("button-press-event", self.copy_code)
        copy_event.add(copy_button)
        h_box.pack_end(copy_event, False, True, 6)

        # Remove button
        remove_event = Gtk.EventBox()
        remove_button = Gtk.Image(xalign=0)
        remove_button.set_from_icon_name(
            "user-trash-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        remove_button.set_tooltip_text(_("Remove the account"))
        remove_event.add(remove_button)
        remove_event.connect("button-press-event",
                             self.parent.remove_account)
        h_box.pack_end(remove_event, False, True, 6)

        self.timer_label.set_label(_("Expires in %s seconds") % self.counter)
        self.timer_label.get_style_context().add_class("account-timer")
        self.code_label.get_style_context().add_class("account-secret-code")
        if self.code_generated:
            self.update_code(self.code_label)
        else:
            self.code_label.set_text(_("Error during the generation of code"))

        self.code_box.pack_end(self.timer_label, False, True, 6)
        self.code_box.pack_start(self.code_label, False, True, 6)
        self.revealer.add(self.code_box)
        self.revealer.set_reveal_child(False)
        self.add(box)

    def get_counter(self):
        return self.counter

    def toggle_code(self, *args):
        self.toggle_code_box()

    def run(self):
        while self.code_generated and self.parent.app.alive and self.alive:
            self.counter -= 1
            if self.counter == 0:
                self.counter = self.counter_max
                self.regenerate_code()
                if self.timer != 0:
                    self.timer = 0
            self.update_timer_label()
            self.changed()
            sleep(1)

    def refresh_listbox(self):
        self.parent.list_box.hide()
        self.parent.list_box.show_all()
        return self.code_generated

    def regenerate_code(self):
        label = self.code_label
        if label:
            self.code.update()
            self.update_code(label)

    def update_code(self, label):
        try:
            code = self.code.get_secret_code()
            if code:
                label.set_text(code)
            else:
                raise TypeError
        except TypeError as e:
            logging.error("Couldn't generate the secret code : %s" % str(e))
            label.set_text(_("Couldn't generate the secret code"))
            self.code_generated = False

    def update_timer_label(self):
        self.timer_label.set_label(_("Expires in %s seconds") % self.counter)
