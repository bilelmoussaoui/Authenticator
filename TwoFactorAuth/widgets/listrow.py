from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject
from TwoFactorAuth.models.code import Code
from TwoFactorAuth.models.authenticator import Authenticator
from TwoFactorAuth.models.settings import SettingsReader
from threading import Thread
from time import sleep
import logging
from math import pi
from gettext import gettext as _


class ListBoxRow(Thread):
    counter_max = 30
    counter = 30
    timer = 0
    code = None
    code_generated = True

    row = None
    code_box = None
    code_label = None
    timer_label = None

    def __init__(self, parent, uid, name, secret_code, logo):
        Thread.__init__(self)
        # Read default values
        cfg = SettingsReader()
        self.counter_max = cfg.read("refresh-time", "preferences")
        self.counter = self.counter_max
        self.parent = parent
        self.id = uid
        self.name = name
        self.secret_code = Authenticator.fetch_secret_code(secret_code)
        if self.secret_code:
            self.code = Code(self.secret_code)
        else:
            self.code_generated = False
            logging.error("Could not read the secret code from, the keyring keys were reset manually")
        self.logo = logo
        self.create_row()
        self.start()
        GObject.timeout_add_seconds(1, self.refresh_listbox)

    @staticmethod
    def get_id(row):
        """
            Get the application id
            :param row: ListBoxRow
            :return: (int): row id
        """
        label_id = row.get_children()[0].get_children()[2]
        label_id = int(label_id.get_text())
        return label_id

    @staticmethod
    def get_label(row):
        """
            Get the application label
            :param row: ListBoxRow
            :return: (str): application label
        """
        label = row.get_children()[0].get_children()[0].get_children()[2].get_children()[0].get_text()
        return label.strip()

    @staticmethod
    def get_code(row):
        code_box = ListBoxRow.get_code_box(row)
        return code_box.get_children()[0].get_text()

    @staticmethod
    def get_code_label(row):
        code_box = ListBoxRow.get_code_box(row)
        return code_box.get_children()[0]

    @staticmethod
    def get_checkbox(row):
        """
            Get ListBowRow's checkbox
            :param row: ListBoxRow
            :return: (Gtk.Checkbox)
        """
        return row.get_children()[0].get_children()[0].get_children()[0]

    @staticmethod
    def get_code_box(row):
        """
            Get code's box
            :param row: ListBoxRow
            :return: (Gtk.Box)
        """
        return row.get_children()[0].get_children()[1]

    @staticmethod
    def toggle_code_box(row):
        """
            Toggle code box
        """
        code_box = ListBoxRow.get_code_box(row)
        is_visible = code_box.get_visible()
        code_box.set_visible(not is_visible)
        code_box.set_no_show_all(is_visible)
        code_box.show_all()

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
        self.row = Gtk.ListBoxRow()
        self.row.get_style_context().add_class("application-list-row")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.code_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.code_box.set_visible(False)

        # ID
        label_id = Gtk.Label()
        label_id.set_text(str(self.id))
        label_id.set_visible(False)
        label_id.set_no_show_all(True)

        box.pack_start(h_box, True, True, 0)
        box.pack_start(self.code_box, True, True, 0)
        box.pack_end(label_id, False, False, 0)

        # Checkbox
        checkbox = Gtk.CheckButton()
        checkbox.set_visible(False)
        checkbox.set_no_show_all(True)
        checkbox.connect("toggled", self.parent.select_application)
        h_box.pack_start(checkbox, False, True, 6)

        # Application logo
        auth_icon = Authenticator.get_auth_icon(self.logo, self.parent.app.pkgdatadir)
        auth_logo = Gtk.Image(xalign=0)
        auth_logo.set_from_pixbuf(auth_icon)
        h_box.pack_start(auth_logo, False, True, 6)

        # Application name
        name_event = Gtk.EventBox()
        application_name = Gtk.Label(xalign=0)
        application_name.get_style_context().add_class("application-name")
        application_name.set_text(self.name)
        name_event.connect("button-press-event", self.toggle_code)
        name_event.add(application_name)
        h_box.pack_start(name_event, True, True, 6)
        # Copy button
        copy_event = Gtk.EventBox()
        copy_button = Gtk.Image(xalign=0)
        copy_button.set_from_icon_name("edit-copy-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        copy_button.set_tooltip_text(_("Copy the generated code"))
        copy_event.connect("button-press-event", self.copy_code)
        copy_event.add(copy_button)
        h_box.pack_end(copy_event, False, True, 6)

        # Remove button
        remove_event = Gtk.EventBox()
        remove_button = Gtk.Image(xalign=0)
        remove_button.set_from_icon_name("user-trash-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        remove_button.set_tooltip_text(_("Remove the application"))
        remove_event.add(remove_button)
        remove_event.connect("button-press-event", self.parent.remove_application)
        h_box.pack_end(remove_event, False, True, 6)

        self.timer_label = Gtk.Label(xalign=0)
        self.timer_label.set_label(_("Expires in %s seconds") % self.counter)
        self.code_label = Gtk.Label(xalign=0)
        self.code_label.get_style_context().add_class("application-secret-code")
        if self.code_generated:
            self.update_code(self.code_label)
        else:
            self.code_label.set_text(_("Error during the generation of code"))
        self.code_box.set_no_show_all(True)
        self.code_box.set_visible(False)
        self.code_box.pack_end(self.timer_label, False, True, 6)
        self.code_box.pack_start(self.code_label, False, True, 6)

        self.row.add(box)

    def get_counter(self):
        return self.counter

    def toggle_code(self, *args):
        ListBoxRow.toggle_code_box(self.row)

    def run(self):
        while self.code_generated and self.parent.app.alive:
            self.counter -= 1
            if self.counter == 0:
                self.counter = self.counter_max
                self.regenerate_code()
                if self.timer != 0:
                    self.timer = 0
            self.update_timer_label()
            self.row.changed()
            sleep(1)

    def get_list_row(self):
        return self.row

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

