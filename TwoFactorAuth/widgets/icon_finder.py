from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import logging
from TwoFactorAuth.widgets.authenticator_logo import AuthenticatorLogoChooser
from TwoFactorAuth.models.code import Code
from TwoFactorAuth.models.authenticator import Authenticator
from gettext import gettext as _


class IconFinderWindow(Gtk.Window):
    selected_image = None

    def __init__(self, window):
        self.parent = window
        self.generate_window()
        self.generate_compenents()
        self.generate_headerbar()
        self.show_all()

    def generate_window(self):
        Gtk.Window.__init__(self, modal=True,
                            destroy_with_parent=True)
        self.connect("delete-event", lambda x, y: self.destroy())
        self.resize(200, 100)
        self.set_border_width(12)
        self.set_size_request(200, 100)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        self.set_transient_for(self.parent)

    def generate_compenents(self):
        mainbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        logo_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        auth_icon = Authenticator.get_auth_icon("image-missing",
                                                self.parent.parent.app.pkgdatadir)
        logo_image = Gtk.Image(xalign=0)
        logo_image.set_from_pixbuf(auth_icon)
        logo_image.get_style_context().add_class("application-logo-add")
        logo_box.pack_start(logo_image, False, False, 0)

        box_entry = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        icon_entry = Gtk.Entry()
        icon_entry.set_margin_top(10)
        icon_entry.connect("changed", self.update_icon)
        box_entry.pack_start(icon_entry, False, False, 0)

        mainbox.pack_start(logo_box, False, True, 6)
        mainbox.pack_end(box_entry, False, True, 6)

        self.add(mainbox)

    def update_icon(self, entry):
        icon_name = entry.get_text()
        theme = Gtk.IconTheme.get_default()
        apply_button = self.hb.get_children()[1].get_children()[0]
        if theme.has_icon(icon_name):
            icon = theme.load_icon(icon_name, 48, 0)
            apply_button.set_sensitive(True)
        else:
            icon = theme.load_icon("image-missing", 48, 0)
            apply_button.set_sensitive(False)
        icon_image = self.get_children()[0].get_children()[0].get_children()[0]
        icon_image.clear()
        icon_image.set_from_pixbuf(icon)

    def update_logo(self, *args):
        img_entry = self.get_children()[0].get_children()[1].get_children()[0]
        self.parent.update_logo(img_entry.get_text().strip())
        self.close_window()

    def generate_headerbar(self):
        self.hb = Gtk.HeaderBar()

        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        cancel_button = Gtk.Button.new_with_label(_("Cancel"))
        cancel_button.connect("clicked", self.close_window)
        cancel_button.get_style_context().add_class("destructive-action")
        left_box.add(cancel_button)

        apply_button = Gtk.Button.new_with_label(_("Select"))
        apply_button.get_style_context().add_class("suggested-action")
        apply_button.connect("clicked", self.update_logo)
        apply_button.set_sensitive(False)
        right_box.add(apply_button)

        self.hb.pack_start(left_box)
        self.hb.pack_end(right_box)
        self.set_titlebar(self.hb)

    def close_window(self, *args):
        self.destroy()
