from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import logging
from gettext import gettext as _
from hashlib import sha256
from TwoFactorAuth.models.settings import SettingsReader


class PasswordWindow(Gtk.Window):

    def __init__(self, window):
        self.parent = window
        self.cfg = SettingsReader()

        self.hb = Gtk.HeaderBar()
        self.apply_button = Gtk.Button.new_with_label(_("Apply"))
        self.new_entry = Gtk.Entry()
        self.new2_entry = Gtk.Entry()
        self.old_entry = Gtk.Entry()

        self.generate_window()
        self.generate_components()
        self.generate_header_bar()

    def generate_window(self):
        Gtk.Window.__init__(self, type=Gtk.WindowType.TOPLEVEL, title=_("Change password"),
                            modal=True, destroy_with_parent=True)
        self.connect("delete-event", self.close_window)
        self.resize(300, 100)
        self.set_border_width(18)
        self.set_size_request(300, 100)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_resizable(False)
        self.set_transient_for(self.parent)
        self.connect("key_press_event", self.on_key_press)

    def show_window(self):
        self.show_all()

    def on_key_press(self, key, key_event):
        """
            Keyboard listener handler
        """
        if Gdk.keyval_name(key_event.keyval) == "Escape":
            self.close_window()

    def generate_components(self):
        """
            Generate window components
        """
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        if len(self.cfg.read("password", "login")) != 0:
            box_old = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
            old_label = Gtk.Label()
            old_label.set_text(_("Old password"))
            self.old_entry.connect("changed", self.on_type_password)
            self.old_entry.set_visibility(False)
            box_old.pack_end(self.old_entry, False, True, 0)
            box_old.pack_end(old_label, False, True, 0)
            box.add(box_old)

        box_new = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
        new_label = Gtk.Label()
        new_label.set_text(_("New password"))

        self.new_entry.connect("changed", self.on_type_password)
        self.new_entry.set_visibility(False)
        box_new.pack_end(self.new_entry, False, True, 0)
        box_new.pack_end(new_label, False, True, 0)

        box_new2 = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
        new2_label = Gtk.Label()
        new2_label.set_text(_("Repeat new password"))
        self.new2_entry.connect("changed", self.on_type_password)
        self.new2_entry.set_visibility(False)
        box_new2.pack_end(self.new2_entry, False, True, 0)
        box_new2.pack_end(new2_label, False, True, 0)

        box.add(box_new)
        box.add(box_new2)

        main_box.pack_start(box, False, True, 6)
        self.add(main_box)

    def update_password(self, *args):
        """
            Update user password
        """
        password = sha256(
            self.new_entry.get_text().encode("utf-8")).hexdigest()
        self.cfg.update("password", password, "login")
        logging.debug("Password changed successfully")
        self.close_window()

    def on_type_password(self, entry):
        """
            Validate the old & new password
        """
        pwd = self.cfg.read("password", "login")
        old_is_ok = True
        if self.new_entry.get_text() != self.new2_entry.get_text():
            self.new_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY,
                                                   "dialog-error-symbolic")
            self.new2_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY,
                                                    "dialog-error-symbolic")
            are_diff = True
        elif len(self.new_entry.get_text()) == 0:
            are_diff = True
        elif len(self.new_entry.get_text()) == 0:
            are_diff = True
        else:
            are_diff = False
        if len(pwd) != 0:
            if sha256(self.old_entry.get_text().encode('utf-8')).hexdigest() != pwd:
                self.old_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY,
                                                       "dialog-error-symbolic")
                old_is_ok = False
            else:
                old_is_ok = True
            if old_is_ok:
                self.old_entry.set_icon_from_icon_name(
                    Gtk.EntryIconPosition.SECONDARY, None)
        if not are_diff:
            self.new_entry.set_icon_from_icon_name(
                Gtk.EntryIconPosition.SECONDARY, None)
            self.new2_entry.set_icon_from_icon_name(
                Gtk.EntryIconPosition.SECONDARY, None)
        self.apply_button.set_sensitive(not are_diff and old_is_ok)

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
        self.apply_button.connect("clicked", self.update_password)
        self.apply_button.set_sensitive(False)
        right_box.add(self.apply_button)

        self.hb.pack_start(left_box)
        self.hb.pack_end(right_box)
        self.set_titlebar(self.hb)

    def close_window(self, *args):
        """
            Close the window
        """
        self.destroy()
