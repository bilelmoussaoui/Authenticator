
from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gio, Gdk, GObject
from TwoFactorAuth.models.code import Code
from threading import Thread
import time

import logging
from math import pi

class ListBoxRow(Thread):
    counter_max = 30
    counter = 30
    timer = 0
    code = None
    code_generated = True

    def __init__(self, parent, id, name, secret_code, logo):
        Thread.__init__(self)
        self.parent = parent
        self.id = id
        self.name = name
        self.secret_code = secret_code
        self.code = Code(secret_code)
        self.logo = logo
        self.create_row()
        self.start()
        GObject.timeout_add_seconds(1, self.refresh_listbox)


    def on_button_press_event(self, widget, event) :
        if event.button == Gdk.EventType._2BUTTON_PRESS:
            # TODO : add double click event
            pass


    def copy_code(self, eventbox, box):
        self.timer = 0
        self.parent.copy_code(eventbox)
        code_box = self.row.get_children()[0].get_children()[1]
        code_box.set_visible(True)
        code_box.set_no_show_all(False)
        code_box.show_all()
        GObject.timeout_add_seconds(1, self.update_timer)


    def update_timer(self, *args):
        self.timer += 1
        if self.timer > 10:
            code_box = self.row.get_children()[0].get_children()[1]
            code_box.set_visible(False)
            code_box.set_no_show_all(True)
        return self.timer <= 10

    def create_row(self):
        self.row = Gtk.ListBoxRow()
        self.row.get_style_context().add_class("application-list-row")
        self.row.connect("button-press-event", self.on_button_press_event)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        pass_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        pass_box.set_visible(False)
        vbox.pack_start(hbox, True, True, 6)
        vbox.pack_start(pass_box, True, True, 6)

        # ID
        label_id = Gtk.Label()
        label_id.set_text(str(self.id))
        label_id.set_visible(False)
        label_id.set_no_show_all(True)
        vbox.pack_end(label_id, False, False, 0)

        # Checkbox
        checkbox = Gtk.CheckButton()
        checkbox.set_visible(False)
        checkbox.set_no_show_all(True)
        checkbox.connect("toggled", self.parent.select_application)
        hbox.pack_start(checkbox, False, True, 6)

        # Provider logo
        provider_logo = self.parent.app.provider.get_provider_image(self.logo)
        hbox.pack_start(provider_logo, False, True, 6)

        # Provider name
        application_name = Gtk.Label(xalign=0)
        application_name.get_style_context().add_class("application-name")
        application_name.set_text(self.name)
        hbox.pack_start(application_name, True, True, 6)
        # Copy button
        copy_event = Gtk.EventBox()
        copy_button = Gtk.Image(xalign=0)
        copy_button.set_from_icon_name("edit-copy-symbolic",
                                       Gtk.IconSize.SMALL_TOOLBAR)
        copy_button.set_tooltip_text("Copy the generated code..")
        copy_event.connect("button-press-event", self.copy_code)
        copy_event.add(copy_button)
        hbox.pack_end(copy_event, False, True, 6)

        # Remove button
        remove_event = Gtk.EventBox()
        remove_button = Gtk.Image(xalign=0)
        remove_button.set_from_icon_name("user-trash-symbolic",
                                         Gtk.IconSize.SMALL_TOOLBAR)
        remove_button.set_tooltip_text("Remove the source..")
        remove_event.add(remove_button)
        remove_event.connect("button-press-event", self.parent.remove_provider)
        hbox.pack_end(remove_event, False, True, 6)

        self.darea = Gtk.DrawingArea()
        self.darea.set_size_request(24, 24)

        code_label = Gtk.Label(xalign=0)
        code_label.get_style_context().add_class("application-secret-code")
        # TODO : show the real secret code
        self.update_code(code_label)
        pass_box.set_no_show_all(True)
        pass_box.pack_end(self.darea, False, True, 6)
        pass_box.pack_start(code_label, False, True, 6)

        self.row.add(vbox)


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
            self.darea.connect("draw", self.expose)
            self.row.changed()
            time.sleep(1)

    def get_listrow(self):
        return self.row

    def refresh_listbox(self):
        self.parent.listbox.hide()
        self.parent.listbox.show_all()
        return self.code_generated

    def regenerate_code(self):
        label = self.row.get_children()[0].get_children()[1].get_children()[0]
        if label:
            self.code.update()
            self.update_code(label)

    def update_code(self, label):
        try:
            code = self.code.get_secret_code()
            if code != None:
                label.set_text(code)
            else:
                raise TypeError
        except TypeError as e:
            logging.error("Canno't generate secret code")
            logging.error(str(e))
            label.set_text("Couldn't generate the secret code")
            self.code_generated = False

    def expose(self, darea, cairo):
        try:
            if self.code_generated:
                cairo.arc(12, 12, 12, 0, (self.counter*2*pi/self.counter_max))
                cairo.set_source_rgba(0, 0, 0, 0.4)
                cairo.fill_preserve()
                if self.counter < self.counter_max/2:
                    cairo.set_source_rgb(0, 0, 0)
                else:
                    cairo.set_source_rgb(1, 1, 1)
                cairo.move_to(8, 15)
                cairo.show_text(str(self.counter))
        except Exception as e:
            logging.error(str(e))
        return False
