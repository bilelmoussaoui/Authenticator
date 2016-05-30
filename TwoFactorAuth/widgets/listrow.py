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

    row = Gtk.ListBoxRow()
    drawing_area = Gtk.DrawingArea()
    code_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

    def __init__(self, parent, id, name, secret_code, logo):
        Thread.__init__(self)
        # Read default values
        cfg = SettingsReader()
        self.counter_max = cfg.read("refresh-time", "preferences")
        self.counter = self.counter_max
        self.parent = parent
        self.id = id
        self.name = name
        self.secret_code = secret_code
        self.code = Code(secret_code)
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

    def toggle_code_box(self, *args):
        """
            Toggle code box
        """
        is_visible = self.code_box.get_visible()
        self.code_box.set_visible(not is_visible)
        self.code_box.set_no_show_all(is_visible)
        self.code_box.show_all()

    def copy_code(self, event_box, box):
        """
            Copy code shows the code box for a while (10s by default)
        """
        self.timer = 0
        self.parent.copy_code(event_box)
        code_box = self.row.get_children()[0].get_children()[1]
        code_box.set_visible(True)
        code_box.set_no_show_all(False)
        code_box.show_all()
        GObject.timeout_add_seconds(1, self.update_timer)

    def update_timer(self, *args):
        """
            Update timer
        """
        self.timer += 1
        if self.timer > 10:
            code_box = self.row.get_children()[0].get_children()[1]
            code_box.set_visible(False)
            code_box.set_no_show_all(True)
        return self.timer <= 10

    def create_row(self):
        """
            Create ListBoxRow
        """
        self.row.get_style_context().add_class("application-list-row")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.code_box.set_visible(False)
        box.pack_start(h_box, True, True, 6)
        box.pack_start(self.code_box, True, True, 6)

        # ID
        label_id = Gtk.Label()
        label_id.set_text(str(self.id))
        label_id.set_visible(False)
        label_id.set_no_show_all(True)
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
        name_event.connect("button-press-event", self.toggle_code_box)
        name_event.add(application_name)
        h_box.pack_start(name_event, True, True, 6)
        # Copy button
        copy_event = Gtk.EventBox()
        copy_button = Gtk.Image(xalign=0)
        copy_button.set_from_icon_name("edit-copy-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        copy_button.set_tooltip_text(_("Copy the generated code.."))
        copy_event.connect("button-press-event", self.copy_code)
        copy_event.add(copy_button)
        h_box.pack_end(copy_event, False, True, 6)

        # Remove button
        remove_event = Gtk.EventBox()
        remove_button = Gtk.Image(xalign=0)
        remove_button.set_from_icon_name("user-trash-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        remove_button.set_tooltip_text(_("Remove the source.."))
        remove_event.add(remove_button)
        remove_event.connect("button-press-event", self.parent.remove_application)
        h_box.pack_end(remove_event, False, True, 6)

        self.drawing_area.set_size_request(24, 24)

        code_label = Gtk.Label(xalign=0)
        code_label.get_style_context().add_class("application-secret-code")
        # TODO : show the real secret code
        self.update_code(code_label)
        self.code_box.set_no_show_all(True)
        self.code_box.pack_end(self.drawing_area, False, True, 6)
        self.code_box.pack_start(code_label, False, True, 6)

        self.row.add(box)

    def get_counter(self):
        return self.counter

    def run(self):
        while self.code_generated and self.parent.app.alive:
            self.counter -= 1
            if self.counter < 0:
                self.counter = self.counter_max
                self.regenerate_code()
                if self.timer != 0:
                    self.timer = 0
            self.drawing_area.connect("draw", self.expose)
            self.row.changed()
            sleep(1)

    def get_list_row(self):
        return self.row

    def refresh_listbox(self):
        self.parent.list_box.hide()
        self.parent.list_box.show_all()
        return self.code_generated

    def regenerate_code(self):
        label = self.row.get_children()[0].get_children()[1].get_children()[0]
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

    def expose(self, drawing_area, cairo):
        try:
            if self.code_generated:
                cairo.arc(12, 12, 12, 0, (self.counter * 2 * pi / self.counter_max))
                cairo.set_source_rgba(0, 0, 0, 0.4)
                cairo.fill_preserve()
                # TODO : get colors from default theme
                if self.counter < self.counter_max / 2:
                    cairo.set_source_rgb(0, 0, 0)
                else:
                    cairo.set_source_rgb(1, 1, 1)
                cairo.move_to(8, 15)
                cairo.show_text(str(self.counter))
        except Exception as e:
            logging.error(str(e))
        return False
