from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk
import logging
from gettext import gettext as _


class ApplicationRow(Gtk.ListBoxRow):

    def __init__(self, name, logo):
        Gtk.ListBoxRow.__init__(self)
        self.name = name
        self.logo = logo
        # Create the list row
        self.create_row()

    def get_name(self):
        """
            Get the application label
            :return: (str): application label
        """
        return self.name

    def create_row(self):
        """
            Create ListBoxRow
        """
        self.get_style_context().add_class("application-list-row")
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        # Application logo
        application_image = Gtk.Image(xalign=0)
        application_image.set_from_pixbuf(self.logo)
        hbox.pack_start(application_image, False, True, 6)

        # Application name
        application_name = Gtk.Label(xalign=0)
        application_name.get_style_context().add_class("application-name")
        application_name.set_text(self.name)
        hbox.pack_start(application_name, True, True, 6)

        vbox.pack_start(hbox, True, True, 6)
        self.add(vbox)
