from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import logging
from TwoFactorAuth.ui.logo_provider import LogoProviderWindow
from TwoFactorAuth.models.code import Code

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] %(message)s',
                    )


class AddProviderWindow(Gtk.Window):
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
        image = directory + image
        img_box = self.get_children()[0].get_children()[0].get_children()
        img_box[0].get_children()[0].clear()
        img_box[0].get_children()[0].set_from_file(image)

    def generate_window(self):
        Gtk.Window.__init__(self, title="Add a new provider", modal=True,
                            destroy_with_parent=True)
        self.connect("delete-event", lambda x, y: self.destroy())
        self.resize(300, 100)
        self.set_border_width(18)
        self.set_size_request(300, 100)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        self.set_transient_for(self.parent)
        self.connect("key_press_event", self.on_key_press)

    def on_key_press(self, provider, keyevent):
        if Gdk.keyval_name(keyevent.keyval) == "Escape":
            self.destroy()

    def select_logo(self, *args):
        LogoProviderWindow(self)

    def add_provider(self, *args):
        entries_box = self.get_children()[0].get_children()[1].get_children()
        name_entry = entries_box[0].get_children()[1].get_text()
        secret_entry = entries_box[1].get_children()[1].get_text()
        image_entry = self.selected_image if self.selected_image else "image-missing"
        try:
            self.parent.app.provider.add_provider(name_entry,
                                                    secret_entry,
                                                    image_entry
                                                )
            id = self.parent.app.provider.get_latest_id()
            self.parent.update_list(id, name_entry, secret_entry, image_entry)
            self.parent.refresh_window()
            self.close_window()
        except Exception as e:
            logging.error("Error in adding a new provider")
            logging.error(str(e))

    def generate_compenents(self):
        mainbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        logo_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        hbox_title = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
        title_label = Gtk.Label()
        title_label.set_text("Provider name : ")
        title_entry = Gtk.Entry()
        hbox_title.pack_start(title_label, False, True, 0)
        hbox_title.pack_end(title_entry, False, True, 0)

        hbox_two_factor = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
        two_factor_label = Gtk.Label()
        two_factor_label.set_text("Two-factor secret : ")
        two_factor_entry = Gtk.Entry()
        two_factor_entry.connect("changed", self.validate_ascii_code)
        hbox_two_factor.pack_start(two_factor_label, False, True, 0)
        hbox_two_factor.pack_end(two_factor_entry, False, True, 0)

        logo_event = Gtk.EventBox()
        logo_image = self.parent.app.provider.get_provider_image("image-missing")
        logo_image.get_style_context().add_class("provider-logo-add")
        logo_event.add(logo_image)
        logo_event.connect("button-press-event", self.select_logo)
        logo_box.pack_start(logo_event, False, False, 6)

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

    def generate_headerbar(self):
        self.hb = Gtk.HeaderBar()

        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        cancel_button = Gtk.Button.new_with_label("Cancel")
        cancel_button.connect("clicked", self.close_window)
        cancel_button.get_style_context().add_class("destructive-action")
        left_box.add(cancel_button)

        apply_button = Gtk.Button.new_with_label("Add")
        apply_button.get_style_context().add_class("suggested-action")
        apply_button.connect("clicked", self.add_provider)
        apply_button.set_sensitive(False)
        right_box.add(apply_button)

        self.hb.pack_start(left_box)
        self.hb.pack_end(right_box)
        self.set_titlebar(self.hb)

    def close_window(self, *args):
        self.destroy()
