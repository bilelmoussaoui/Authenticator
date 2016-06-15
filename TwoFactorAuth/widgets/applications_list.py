from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gio, Gdk
from TwoFactorAuth.widgets.search_bar import SearchBar
from TwoFactorAuth.widgets.application_row import ApplicationRow
from os import path, listdir, environ as env
from TwoFactorAuth.utils import get_icon
from gettext import gettext as _


class ApplicationChooserWindow(Gtk.Window):

    def __init__(self, window):
        # directory that contains the main icons

        directory = path.join(env.get("DATA_DIR"), "applications") + "/"
        self.logos = listdir(directory)
        self.logos.sort()
        self.parent = window

        self.search_button = Gtk.ToggleButton()
        self.listbox = Gtk.ListBox()
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.generate_window()
        self.generate_search_bar()
        self.generate_components()
        self.generate_header_bar()

    def generate_window(self):
        """
            Generate the main window
        """
        Gtk.Window.__init__(self, type=Gtk.WindowType.TOPLEVEL, modal=True,
                            destroy_with_parent=True)
        self.connect("destroy", self.close_window)
        self.resize(410, 550)
        self.set_size_request(410, 550)
        x, y = self.parent.parent.get_position()
        self.move(x, y)
        self.set_resizable(False)
        self.set_transient_for(self.parent)
        self.connect("key_press_event", self.on_key_press)
        self.add(self.main_box)

    def generate_components(self):
        """
            Generate window compenents
        """
        box_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        if len(self.logos) > 0:
            # Create a ScrolledWindow for installed applications
            scrolled_win = Gtk.ScrolledWindow()
            scrolled_win.add_with_viewport(box_outer)
            self.main_box.pack_start(scrolled_win, True, True, 0)

            self.listbox.get_style_context().add_class("applications-list")
            self.listbox.set_adjustment()
            self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
            box_outer.pack_start(self.listbox, True, True, 0)
            i = 0
            while i < len(self.logos):
                img_path = self.logos[i]
                app_name = path.splitext(img_path)[0].strip(".").title()
                # Application logo
                app_logo = get_icon(img_path)
                self.listbox.add(ApplicationRow(app_name, app_logo))
                i += 1

    def generate_header_bar(self):
        """
            Generate header bar box
        """
        self.hb = Gtk.HeaderBar()
        self.hb.props.title = _("Select an application")

        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        cancel_button = Gtk.Button.new_with_label(_("Cancel"))
        cancel_button.connect("clicked", self.close_window)
        cancel_button.get_style_context().add_class("destructive-action")
        left_box.add(cancel_button)

        search_icon = Gio.ThemedIcon(name="system-search-symbolic")
        search_image = Gtk.Image.new_from_gicon(
            search_icon, Gtk.IconSize.BUTTON)
        self.search_button.set_tooltip_text(_("Search"))
        self.search_button.set_image(search_image)

        next_button = Gtk.Button.new_with_label(_("Next"))
        next_button.get_style_context().add_class("suggested-action")
        next_button.connect("clicked", self.select_logo)

        right_box.pack_start(self.search_button, False, False, 6)
        right_box.pack_start(next_button, False, False, 6)

        self.hb.pack_end(right_box)
        self.hb.pack_start(left_box)
        self.set_titlebar(self.hb)

    def generate_search_bar(self):
        """
            Generate the search bar
        """
        self.search_bar = SearchBar(self.listbox)
        self.search_button.connect("toggled", self.search_bar.toggle)

        self.main_box.pack_start(self.search_bar, False, True, 0)

    def on_key_press(self, label, key_event):
        """
            Keyboard listener handling
        """
        key_pressed = Gdk.keyval_name(key_event.keyval).lower()
        if key_pressed == "escape":
            if self.search_bar.is_visible():
                self.search_bar.toggle()
            else:
                self.close_window()
        elif key_pressed == "f":
            if key_event.state == Gdk.ModifierType.CONTROL_MASK:
                self.search_button.set_active(
                    not self.search_button.get_active())
        elif key_pressed == "return":
            self.select_logo()

    def select_logo(self, *args):
        """
            Select a logo and return its path to the add application window
        """
        index = self.listbox.get_selected_row().get_index()
        if len(self.logos) > 0:
            img_path = self.logos[index]
            self.parent.update_logo(img_path)
            self.parent.show_window()
            self.close_window()

    def show_window(self):
        self.show_all()

    def close_window(self, *args):
        """
            Close the window
        """
        self.destroy()
