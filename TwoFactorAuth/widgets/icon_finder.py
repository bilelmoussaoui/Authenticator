from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from TwoFactorAuth.models.authenticator import Authenticator
from gettext import gettext as _


class IconFinderWindow(Gtk.Window):
    selected_image = None
    hb = Gtk.HeaderBar()
    apply_button = Gtk.Button.new_with_label(_("Select"))
    logo_image = Gtk.Image(xalign=0)
    icon_entry = Gtk.Entry()

    def __init__(self, window):
        self.parent = window
        self.generate_window()
        self.generate_components()
        self.generate_header_bar()
        self.show_all()

    def generate_window(self):
        Gtk.Window.__init__(self, modal=True, destroy_with_parent=True)
        self.connect("delete-event", self.close_window)
        self.resize(200, 100)
        self.set_border_width(12)
        self.set_size_request(200, 100)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        self.set_transient_for(self.parent)
        self.connect("key_press_event", self.on_key_press)

    def on_key_press(self, key, key_event):
        """
            Keyboard Listener handler
        """
        if Gdk.keyval_name(key_event.keyval) == "Escape":
            self.close_window()

    def generate_components(self):
        """
            Generate all the components
        """
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        logo_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        auth_icon = Authenticator.get_auth_icon("image-missing",
                                                self.parent.parent.app.pkgdatadir)
        self.logo_image.set_from_pixbuf(auth_icon)
        self.logo_image.get_style_context().add_class("application-logo-add")
        logo_box.pack_start(self.logo_image, False, False, 0)

        box_entry = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.icon_entry.set_margin_top(10)
        self.icon_entry.connect("changed", self.update_icon)
        box_entry.pack_start(self.icon_entry, False, False, 0)

        main_box.pack_start(logo_box, False, True, 6)
        main_box.pack_end(box_entry, False, True, 6)

        self.add(main_box)

    def update_icon(self, entry):
        """
            Update icon image on changed event
        """
        icon_name = entry.get_text()
        theme = Gtk.IconTheme.get_default()
        apply_button = self.hb.get_children()[1].get_children()[0]
        if theme.has_icon(icon_name):
            icon = theme.load_icon(icon_name, 48, 0)
            apply_button.set_sensitive(True)
        else:
            icon = theme.load_icon("image-missing", 48, 0)
            apply_button.set_sensitive(False)
        self.logo_image.clear()
        self.logo_image.set_from_pixbuf(icon)

    def update_logo(self, *args):
        """
            Update application logo and close the window
        """
        self.parent.update_logo(self.icon_entry.get_text().strip())
        self.close_window()

    def generate_header_bar(self):
        """
            Generate header bar box
        """
        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        cancel_button = Gtk.Button.new_with_label(_("Cancel"))
        cancel_button.connect("clicked", self.close_window)
        cancel_button.get_style_context().add_class("destructive-action")
        left_box.add(cancel_button)

        self.apply_button.get_style_context().add_class("suggested-action")
        self.apply_button.connect("clicked", self.update_logo)
        self.apply_button.set_sensitive(False)
        right_box.add(self.apply_button)

        self.hb.pack_start(left_box)
        self.hb.pack_end(right_box)
        self.set_titlebar(self.hb)

    def close_window(self, *args):
        """
            Close the window
        """
        self.hide()
        return True
