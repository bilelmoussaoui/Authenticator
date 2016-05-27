from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gio, Gdk
import logging
from os import path, listdir
logging.basicConfig(level=logging.DEBUG,
                format='[%(levelname)s] %(message)s',
                )
class LogoProviderWindow(Gtk.Window):

    def __init__(self, window):
        directory = window.parent.app.pkgdatadir + "/data/logos/"
        self.logos = listdir(directory)
        self.logos.sort()
        self.window = window
        self.generate_window()
        self.genereate_searchbar()
        self.generate_compenents()
        self.generate_headerbar()
        self.show_all()
        Gtk.main()

    def generate_window(self):
        Gtk.Window.__init__(self, title="Add a new provider", modal=True,
                            destroy_with_parent=True)
        self.connect("delete-event", lambda x, y: self.destroy())
        self.resize(350, 400)
        self.set_size_request(350, 400)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        self.set_transient_for(self.window.parent)
        self.connect("key_press_event", self.on_key_press)
        self.add(Gtk.Box(orientation=Gtk.Orientation.VERTICAL))

    def filter_func(self, row, data, notify_destroy):
        provider_label = row.get_children()[0].get_children()[0].get_children()
        data = data.strip().lower()
        if len(data) > 0:
            return data in provider_label[1].get_text().lower()
        else:
            return True

    def filter_providers(self, entry):
        data = entry.get_text()
        if len(data) != 0:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY,
                                                "edit-clear-symbolic")
        else:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY,
                                            None)
        self.listbox.set_filter_func(self.filter_func, data, False)

    def on_key_press(self, provider, keyevent):
        CONTROL_MASK = Gdk.ModifierType.CONTROL_MASK
        keypressed = Gdk.keyval_name(keyevent.keyval).lower()
        if keypressed == "escape":
            self.destroy()
        elif keypressed == "f":
            if keyevent.state == CONTROL_MASK:
                search_box = self.get_children()[0].get_children()[0]
                is_visible = search_box.get_no_show_all()
                search_box.set_no_show_all(not is_visible)
                search_box.set_visible(is_visible)
                search_box.show_all()
                if is_visible:
                    search_box.get_children()[0].grab_focus_without_selecting()
                else:
                    self.listbox.set_filter_func(lambda x,y,z : True, None, False)
        elif keypressed == "return":
            self.select_logo()

    def genereate_searchbar(self):
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hbox.set_margin_left(60)

        search_entry = Gtk.Entry()
        search_entry.connect("changed", self.filter_providers)
        search_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY,
                                    "system-search-symbolic")

        hbox.pack_start(search_entry, False, True, 6)
        hbox.set_visible(False)
        self.get_children()[0].pack_start(hbox, False, True, 6)
        self.get_children()[0].get_children()[0].set_no_show_all(True)

    def select_logo(self, *args):
        index = self.listbox.get_selected_row().get_index()
        if len(self.logos) > 0:
            img_path = self.logos[index]
            self.window.update_logo(img_path)
            self.close_window()

    def generate_compenents(self):
        box_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        directory = "/home/bilal/Projects/Two-factor-gtk/data/logos/"
        if len(self.logos) > 0:
            # Create a ScrolledWindow for installed applications
            scrolled_win = Gtk.ScrolledWindow()
            scrolled_win.add_with_viewport(box_outer)
            self.get_children()[0].pack_start(scrolled_win, True, True, 0)

            self.listbox = Gtk.ListBox()
            self.listbox.get_style_context().add_class("applications-list")
            self.listbox.set_adjustment()
            self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
            box_outer.pack_start(self.listbox, True, True, 0)
            i = 0
            while i < len(self.logos):
                logo = self.logos[i]
                provider_name = path.splitext(logo)[0].strip(".").title()
                row = Gtk.ListBoxRow()
                row.get_style_context().add_class("application-list-row")
                vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

                # Provider logo
                provider = self.window.parent.app.provider
                provider_logo = provider.get_provider_image(logo)
                hbox.pack_start(provider_logo, False, True, 6)

                # Provider name
                application_name = Gtk.Label(xalign=0)
                application_name.get_style_context().add_class("application-name")
                application_name.set_text(provider_name)
                hbox.pack_start(application_name, True, True, 6)

                vbox.pack_start(hbox, True, True, 6)
                row.add(vbox)
                self.listbox.add(row)
                i += 1

    def generate_headerbar(self):
        self.hb = Gtk.HeaderBar()

        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        cancel_button = Gtk.Button.new_with_label("Cancel")
        cancel_button.connect("clicked", self.close_window)
        cancel_button.get_style_context().add_class("destructive-action")
        left_box.add(cancel_button)

        apply_button = Gtk.Button.new_with_label("Choose")
        apply_button.get_style_context().add_class("suggested-action")
        apply_button.connect("clicked", self.select_logo)
        right_box.add(apply_button)

        self.hb.pack_start(left_box)
        self.hb.pack_end(right_box)
        self.set_titlebar(self.hb)

    def close_window(self, *args):
        self.destroy()
