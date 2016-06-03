from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gio, Gdk
from TwoFactorAuth.models.authenticator import Authenticator
from os import path, listdir
from gettext import gettext as _


class ApplicationChooserWindow(Gtk.Window):

    def __init__(self, window):
        # directory that contains the main icons
        directory = window.parent.app.pkgdatadir + "/data/logos/"
        self.logos = listdir(directory)
        self.logos.sort()
        self.parent = window
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.generate_window()
        self.generate_search_bar()
        self.generate_components()
        self.generate_header_bar()

    def generate_window(self):
        """
            Generate the main window
        """
        Gtk.Window.__init__(self, type=Gtk.WindowType.TOPLEVEL, modal=True, destroy_with_parent=True)
        self.connect("destroy", self.close_window)
        self.resize(410, 550)
        self.set_size_request(410, 550)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
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

            self.listbox = Gtk.ListBox()
            self.listbox.get_style_context().add_class("applications-list")
            self.listbox.set_adjustment()
            self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
            box_outer.pack_start(self.listbox, True, True, 0)
            i = 0
            while i < len(self.logos):
                img_path = self.logos[i]
                app_name = path.splitext(img_path)[0].strip(".").title()
                row = Gtk.ListBoxRow()
                row.get_style_context().add_class("application-list-row")
                vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

                # Application logo
                auth_icon = Authenticator.get_auth_icon(img_path,
                                                        self.parent.parent.app.pkgdatadir)
                auth_img = Gtk.Image(xalign=0)
                auth_img.set_from_pixbuf(auth_icon)
                hbox.pack_start(auth_img, False, True, 6)

                # Application name
                application_name = Gtk.Label(xalign=0)
                application_name.get_style_context().add_class("application-name")
                application_name.set_text(app_name)
                hbox.pack_start(application_name, True, True, 6)

                vbox.pack_start(hbox, True, True, 6)
                row.add(vbox)
                self.listbox.add(row)
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

        next_button = Gtk.Button.new_with_label(_("Next"))
        next_button.get_style_context().add_class("suggested-action")
        next_button.connect("clicked", self.select_logo)
        right_box.add(next_button)

        self.hb.pack_start(left_box)
        self.hb.pack_end(right_box)
        self.set_titlebar(self.hb)

    def generate_search_bar(self):
        """
            Generate the search bar
        """
        self.search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.search_entry = Gtk.Entry()
        self.search_entry.connect("changed", self.filter_logos)
        self.search_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, "system-search-symbolic")

        self.search_box.set_visible(False)
        self.search_box.set_no_show_all(True)
        box.pack_start(self.search_entry, False, True, 6)

        self.search_box.pack_start(box, True, False, 6)
        self.main_box.pack_start(self.search_box, False, False, 6)

    def on_key_press(self, label, key_event):
        """
            Keyboard listener handling
        """
        key_pressed = Gdk.keyval_name(key_event.keyval).lower()
        if key_pressed == "escape":
            if self.search_box.get_visible():
                self.toggle_search_box()
            else:
                self.close_window()
        elif key_pressed == "f":
            if key_event.state == Gdk.ModifierType.CONTROL_MASK:
                self.toggle_search_box()
        elif key_pressed == "return":
            self.select_logo()

    def filter_func(self, row, data, notify_destroy):
        """
            Filter the result of research
        """
        app_label = row.get_children()[0].get_children()[0].get_children()
        data = data.strip().lower()
        if len(data) > 0:
            return data in app_label[1].get_text().lower()
        else:
            return True

    def filter_logos(self, entry):
        """
            Filter logos
        """
        data = entry.get_text()
        if len(data) != 0:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY,
                                          "edit-clear-symbolic")
            entry.connect("icon-press", self.on_icon_pressed)
        else:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY,
                                          None)
        self.listbox.set_filter_func(self.filter_func, data, False)

    def on_icon_pressed(self, entry, icon_pos, event):
        """
            Remove icon click event
        """
        if icon_pos == Gtk.EntryIconPosition.SECONDARY:
            entry.set_text("")

    def toggle_search_box(self):
        """
            Toggle the visibility of the search box
        """
        is_visible = self.search_box.get_no_show_all()
        self.search_box.set_no_show_all(not is_visible)
        self.search_box.set_visible(is_visible)
        self.search_box.show_all()
        if is_visible:
            self.search_entry.grab_focus_without_selecting()
        else:
            self.listbox.set_filter_func(
                lambda x, y, z: True, None, False)

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
