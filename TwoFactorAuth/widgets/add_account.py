from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import logging
from TwoFactorAuth.widgets.applications_list import ApplicationChooserWindow
from TwoFactorAuth.models.code import Code
from TwoFactorAuth.models.authenticator import Authenticator
from gettext import gettext as _


class AddAccount(Gtk.Window):

    def __init__(self, window):
        self.parent = window
        
        self.selected_image = None
        self.step = 1
        self.logo_image = Gtk.Image(xalign=0)
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
        self.resize(410, 300)
        self.set_border_width(18)
        self.set_size_request(410, 300)
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
        self.apply_button.connect("clicked", self.add_application)
        self.apply_button.set_sensitive(False)
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
        hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
        title_label = Gtk.Label()
        title_label.set_text(_("Account Name"))

        hbox_title.pack_end(self.name_entry, False, True, 0)
        hbox_title.pack_end(title_label, False, True, 0)

        hbox_two_factor = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
        two_factor_label = Gtk.Label()
        two_factor_label.set_text(_("Secret Code"))
        self.secret_code.connect("changed", self.validate_ascii_code)

        hbox_two_factor.pack_end(self.secret_code, False, True, 0)
        hbox_two_factor.pack_end(two_factor_label, False, True, 0)

        auth_icon = Authenticator.get_auth_icon("image-missing", self.parent.app.pkgdatadir)
        self.logo_image.set_from_pixbuf(auth_icon)
        self.logo_image.get_style_context().add_class("application-logo-add")
        logo_box.pack_start(self.logo_image, True, False, 6)
        logo_box.set_property("margin-bottom", 20)

        vbox.add(hbox_title)
        vbox.add(hbox_two_factor)
        labels_box.pack_start(vbox, True, False, 6)
        main_box.pack_start(logo_box, False, True, 6)
        main_box.pack_start(labels_box, False, True, 6)
        self.add(main_box)

    def on_key_press(self, key, key_event):
        """
            Keyboard Listener handler
        """
        if Gdk.keyval_name(key_event.keyval) == "Escape":
            self.close_window()

    def update_logo(self, image):
        """
            Update image logo
        """
        directory = self.parent.app.pkgdatadir + "/data/logos/"
        self.selected_image = image
        auth_icon = Authenticator.get_auth_icon(image, self.parent.app.pkgdatadir)
        self.logo_image.clear()
        self.logo_image.set_from_pixbuf(auth_icon)

    def validate_ascii_code(self, entry):
        """
            Validate if the typed secret code is a valid ascii one
        """
        ascii_code = entry.get_text().strip()
        is_valid = Code.is_valid(ascii_code)
        self.apply_button.set_sensitive(is_valid)
        if not is_valid and len(ascii_code) != 0:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "dialog-error-symbolic")
        else:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, None)

    def add_application(self, *args):
        """
            Add a new application to the database
        """
        name_entry = self.name_entry.get_text()
        secret_entry = self.secret_code.get_text()
        image_entry = self.selected_image if self.selected_image else "image-missing"
        try:
            self.parent.app.auth.add_application(name_entry, secret_entry,
                                                 image_entry)
            uid = self.parent.app.auth.get_latest_id()
            self.parent.append_list_box(uid, name_entry, secret_entry, image_entry)
            self.parent.refresh_window()
            self.close_window()
        except Exception as e:
            logging.error("Error in adding a new application")
            logging.error(str(e))

    def show_window(self):
        if self.step == 1:
            applications_choose_window = ApplicationChooserWindow(self)
            applications_choose_window.show_window()
            self.step = 2
        else:
            self.show_all()

    def close_window(self, *args):
        """
            Close the window
        """
        self.destroy()
