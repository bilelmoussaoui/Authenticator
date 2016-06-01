from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import logging
from TwoFactorAuth.widgets.authenticator_logo import AuthenticatorLogoChooser
from TwoFactorAuth.models.code import Code
from TwoFactorAuth.models.authenticator import Authenticator
from gettext import gettext as _


class AddAuthenticator(Gtk.Window):
    selected_image = None
    hb = Gtk.HeaderBar()

    popover = Gtk.PopoverMenu.new()
    logo_image = Gtk.Image(xalign=0)
    secret_code = Gtk.Entry()
    name_entry = Gtk.Entry()

    logo_finder_window = None
    provided_icons_window = None

    def __init__(self, window):
        self.parent = window
        self.generate_window()
        self.generate_components()
        self.generate_header_bar()
        self.show_all()

    def generate_window(self):
        Gtk.Window.__init__(self, title=_("Add a new application"),
                            modal=True, destroy_with_parent=True)
        self.connect("delete-event", self.close_window)
        self.resize(430, 350)
        self.set_border_width(18)
        self.set_size_request(430, 350)
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

    def update_logo(self, image):
        """
            Update image logo
        """
        directory = self.parent.app.pkgdatadir + "/data/logos/"
        self.selected_image = image
        auth_icon = Authenticator.get_auth_icon(image, self.parent.app.pkgdatadir)
        self.logo_image.clear()
        self.logo_image.set_from_pixbuf(auth_icon)

    def select_logo(self, event_box, event_button):
        """
            Application logo selection, right & left mouse click event handling
        """
        # Right click handling
        if event_button.button == 3:
            if self.popover.get_visible():
                self.popover.hide()
            else:
                self.popover.show_all()
        else:
            AuthenticatorLogoChooser(self)

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
        title_label.set_text(_("Application Name"))

        hbox_title.pack_end(self.name_entry, False, True, 0)
        hbox_title.pack_end(title_label, False, True, 0)

        hbox_two_factor = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
        two_factor_label = Gtk.Label()
        two_factor_label.set_text(_("Secret Code"))
        self.secret_code.connect("changed", self.validate_ascii_code)

        hbox_two_factor.pack_end(self.secret_code, False, True, 0)
        hbox_two_factor.pack_end(two_factor_label, False, True, 0)


        self.hbox_icon_name = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
        icon_name_label = Gtk.Label()
        self.icon_name_entry = Gtk.Entry()
        icon_name_label.set_text(_("Icon name"))
        self.icon_name_entry.connect("changed", self.validate_icon_name)
        self.hbox_icon_name.pack_end(self.icon_name_entry, False, True, 0)
        self.hbox_icon_name.pack_end(icon_name_label, False, True, 0)
        self.hbox_icon_name.set_visible(False)
        self.hbox_icon_name.set_no_show_all(True)

        logo_event = Gtk.EventBox()
        auth_icon = Authenticator.get_auth_icon("image-missing", self.parent.app.pkgdatadir)
        self.logo_image.set_from_pixbuf(auth_icon)
        self.logo_image.get_style_context().add_class("application-logo-add")
        logo_event.add(self.logo_image)
        logo_event.connect("button-press-event", self.select_logo)
        logo_box.pack_start(logo_event, True, False, 6)
        logo_box.set_property("margin-bottom", 20)

        self.popover.get_style_context().add_class("choose-popover")
        self.popover.set_relative_to(self.logo_image)

        pbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        pbox.set_property('margin', 12)
        pbox.set_property('width-request', 150)
        self.popover.add(pbox)

        provided = Gtk.ModelButton.new()
        provided.set_label(_("Select from provided icons"))
        provided.connect("clicked", self.on_provided_click)
        pbox.pack_start(provided, False, False, 0)

        file = Gtk.ModelButton.new()
        file.set_label(_("Select a file"))
        file.connect("clicked", self.on_file_clicked)
        pbox.pack_start(file, False, False, 0)

        icon_name = Gtk.ModelButton.new()
        icon_name.set_label(_("Select an icon name"))
        icon_name.connect("clicked", self.on_icon_clicked)
        pbox.pack_start(icon_name, False, False, 0)

        vbox.add(hbox_title)
        vbox.add(hbox_two_factor)
        vbox.add(self.hbox_icon_name)
        labels_box.pack_start(vbox, True, False, 6)
        main_box.pack_start(logo_box, False, True, 6)
        main_box.pack_start(labels_box, False, True, 6)
        self.add(main_box)

    def validate_icon_name(self, entry):
        icon_name = entry.get_text()
        theme = Gtk.IconTheme.get_default()
        if theme.has_icon(icon_name):
            icon = theme.load_icon(icon_name, 48, 0)
            self.selected_image = icon_name
        else:
            icon = theme.load_icon("image-missing", 48, 0)
        self.logo_image.clear()
        self.logo_image.set_from_pixbuf(icon)

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

    def on_provided_click(self, *args):
        """
            Select an icon from provided ones
        """
        if self.provided_icons_window:
            self.provided_icons_window.show()
        else:
            self.provided_icons_window = AuthenticatorLogoChooser(self)

    def on_file_clicked(self, *args):
        """"
            Select an icon by filename
        """
        dialog = Gtk.FileChooserDialog(_("Please choose a file"), self,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.update_logo(dialog.get_filename())
        dialog.destroy()

    def on_icon_clicked(self, *args):
        """
            Shows icon finder window
            select icon by icon name
        """
        is_visible = self.hbox_icon_name.get_no_show_all()
        self.hbox_icon_name.set_visible(is_visible)
        self.hbox_icon_name.set_no_show_all(not is_visible)
        self.hbox_icon_name.show_all()

    def add_filters(self, dialog):
        """
            Add file filters to GtkFileChooser
        """
        filter_png = Gtk.FileFilter()
        filter_png.set_name("PNG")
        filter_png.add_mime_type("image/png")
        dialog.add_filter(filter_png)

        filter_svg = Gtk.FileFilter()
        filter_svg.set_name("SVG")
        filter_svg.add_mime_type("image/svg+xml")
        dialog.add_filter(filter_svg)

    def generate_header_bar(self):
        """
            Generate the header bar box
        """
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

    def close_window(self, *args):
        """
            Close the window
        """
        self.hide()
        return True
