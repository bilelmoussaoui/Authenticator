from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio
import logging


class SearchBar(Gtk.Box):

    def __init__(self, list_accounts):
        self.search_entry = Gtk.Entry()
        self.list_accounts = list_accounts
        self.generate()

    def generate(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.revealer = Gtk.Revealer()
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self.search_entry.set_width_chars(28)
        self.search_entry.connect("changed", self.filter_applications)
        self.search_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY,
                                                  "system-search-symbolic")

        box.pack_start(self.search_entry, True, False, 12)
        box.props.margin = 6
        self.revealer.add(box)
        self.revealer.set_reveal_child(False)
        self.pack_start(self.revealer, True, False, 0)

    def toggle(self, *args):
        if self.revealer.get_reveal_child():
            self.revealer.set_reveal_child(False)
            self.search_entry.set_text("")
            self.list_accounts.set_filter_func(lambda x, y, z: True,
                                               None, False)
        else:
            self.revealer.set_reveal_child(True)
            self.search_entry.grab_focus_without_selecting()

    def filter_func(self, row, data, notify_destroy):
        """
            Filter function, used to check if the entered data exists on the application ListBox
        """
        app_label = row.get_name()
        data = data.lower()
        if len(data) > 0:
            return data in app_label.lower()
        else:
            return True

    def is_visible(self):
        return self.revealer.get_reveal_child()

    def is_empty(self):
        return len(self.search_entry.get_text()) == 0

    def on_icon_pressed(self, entry, icon_pos, event):
        if icon_pos == Gtk.EntryIconPosition.SECONDARY:
            self.search_entry.set_text("")

    def filter_applications(self, entry):
        data = entry.get_text().strip()
        if len(data) != 0:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY,
                                          "edit-clear-symbolic")
            entry.connect("icon-press", self.on_icon_pressed)
        else:
            entry.set_icon_from_icon_name(
                Gtk.EntryIconPosition.SECONDARY, None)
        self.list_accounts.set_filter_func(self.filter_func, data, False)
