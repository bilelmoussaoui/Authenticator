from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import logging
from TwoFactorAuth.widgets.authenticator_logo import AuthenticatorLogoChooser
from TwoFactorAuth.widgets.icon_finder import IconFinderWindow
from TwoFactorAuth.models.code import Code
from TwoFactorAuth.models.authenticator import Authenticator
from gettext import gettext as _

class AddAuthenticator(Gtk.Window):
    selected_image = None

    def __init__(self, window):
        self.parent = window
        self.generate_window()
        self.generate_compenents()
        self.generate_headerbar()
        self.show_all()


    def update_logo(self, image):
        # TODO : add the possiblity to use external icons or icon names
        directory = self.parent.app.pkgdatadir + "/data/logos/"
        self.selected_image = image
        auth_icon = Authenticator.get_auth_icon(image, self.parent.app.pkgdatadir)
        img_box = self.get_children()[0].get_children()[0].get_children()
        img_box[0].get_children()[0].clear()
        img_box[0].get_children()[0].set_from_pixbuf(auth_icon)

    def generate_window(self):
        Gtk.Window.__init__(self, title=_("Add a new application"), modal=True,
                            destroy_with_parent=True)
        self.connect("delete-event", lambda x, y: self.destroy())
        self.resize(300, 100)
        self.set_border_width(12)
        self.set_size_request(300, 100)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        self.set_transient_for(self.parent)
        self.connect("key_press_event", self.on_key_press)

    def on_key_press(self, key, keyevent):
        if Gdk.keyval_name(keyevent.keyval) == "Escape":
            self.destroy()

    def select_logo(self, eventbox, event_button):
        # Right click handling
        if event_button.button == 3:
            if self.popover.get_visible():
                self.popover.hide()
            else:
                self.popover.show_all()
        else:
            AuthenticatorLogoChooser(self)

    def add_application(self, *args):
        entries_box = self.get_children()[0].get_children()[1].get_children()
        name_entry = entries_box[0].get_children()[1].get_text()
        secret_entry = entries_box[1].get_children()[1].get_text()
        image_entry = self.selected_image if self.selected_image else "image-missing"
        try:
            self.parent.app.auth.add_application(name_entry,secret_entry,
                                                image_entry)
            id = self.parent.app.auth.get_latest_id()
            self.parent.update_list(id, name_entry, secret_entry, image_entry)
            self.parent.refresh_window()
            self.close_window()
        except Exception as e:
            logging.error("Error in adding a new application")
            logging.error(str(e))

    def generate_compenents(self):
        mainbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        logo_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        hbox_title = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
        title_label = Gtk.Label()
        title_label.set_text(_("Application name : "))
        title_entry = Gtk.Entry()
        hbox_title.pack_start(title_label, False, True, 0)
        hbox_title.pack_end(title_entry, False, True, 0)

        hbox_two_factor = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
        two_factor_label = Gtk.Label()
        two_factor_label.set_text(_("Two-factor secret : "))
        two_factor_entry = Gtk.Entry()
        two_factor_entry.connect("changed", self.validate_ascii_code)
        hbox_two_factor.pack_start(two_factor_label, False, True, 0)
        hbox_two_factor.pack_end(two_factor_entry, False, True, 0)

        logo_event = Gtk.EventBox()
        auth_icon = Authenticator.get_auth_icon("image-missing",
                                                self.parent.app.pkgdatadir)
        logo_image = Gtk.Image(xalign=0)
        logo_image.set_from_pixbuf(auth_icon)
        logo_image.get_style_context().add_class("application-logo-add")
        logo_event.add(logo_image)
        logo_event.connect("button-press-event", self.select_logo)
        logo_box.pack_start(logo_event, False, False, 6)

        self.popover = Gtk.PopoverMenu.new()
        self.popover.get_style_context().add_class("choose-popover")
        self.popover.set_relative_to(logo_image)

        pbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.popover.add(pbox)

        provided = Gtk.ModelButton.new()
        provided.set_label(_("Select from provided icons"))
        provided.connect("clicked", self.on_provided_click)
        pbox.pack_start(provided, False, False, 6)

        file = Gtk.ModelButton.new()
        file.set_label(_("Select a file"))
        file.connect("clicked", self.on_file_clicked)
        pbox.pack_start(file, False, False, 6)

        icon_name = Gtk.ModelButton.new()
        icon_name.set_label(_("Select an icon name"))
        icon_name.connect("clicked", self.on_icon_clicked)
        pbox.pack_start(icon_name, False, False, 6)

        vbox.add(hbox_title)
        vbox.add(hbox_two_factor)
        mainbox.pack_start(logo_box, False, True, 6)
        mainbox.pack_start(vbox, False, True, 6)
        self.add(mainbox)

    def validate_ascii_code(self, entry):
        ascii_code = entry.get_text().strip()
        is_valid = Code.is_valid(ascii_code)
        self.hb.get_children()[1].get_children()[0].set_sensitive(is_valid)
        if not is_valid and len(ascii_code) != 0:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY,
                                            "dialog-error-symbolic")
        else:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY,
                                            "")

    def on_provided_click(self, *args):
         AuthenticatorLogoChooser(self)

    def on_file_clicked(self, *args):
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
        IconFinderWindow(self)


    def add_filters(self, dialog):
        filter_png = Gtk.FileFilter()
        filter_png.set_name("PNG")
        filter_png.add_mime_type("image/png")
        dialog.add_filter(filter_png)

        filter_svg = Gtk.FileFilter()
        filter_svg.set_name("SVG")
        filter_svg.add_mime_type("image/svg+xml")
        dialog.add_filter(filter_svg)


    def generate_headerbar(self):
        self.hb = Gtk.HeaderBar()

        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        cancel_button = Gtk.Button.new_with_label(_("Cancel"))
        cancel_button.connect("clicked", self.close_window)
        cancel_button.get_style_context().add_class("destructive-action")
        left_box.add(cancel_button)

        apply_button = Gtk.Button.new_with_label(_("Add"))
        apply_button.get_style_context().add_class("suggested-action")
        apply_button.connect("clicked", self.add_application)
        apply_button.set_sensitive(False)
        right_box.add(apply_button)

        self.hb.pack_start(left_box)
        self.hb.pack_end(right_box)
        self.set_titlebar(self.hb)

    def close_window(self, *args):
        self.destroy()
