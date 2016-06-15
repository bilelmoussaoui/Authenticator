from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, Gdk, GObject, GLib
import logging
from hashlib import sha256
from gettext import gettext as _

class LoginWindow(Gtk.Box):
    password_entry = None
    unlock_button = None

    def __init__(self, application):
        self.app = application
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        self.password_entry = Gtk.Entry()
        self.unlock_button = Gtk.Button()
        self.generate_box()

    def generate_box(self):
        password_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.password_entry.set_visibility(False)
        self.password_entry.set_placeholder_text(_("Enter your password"))
        password_box.pack_start(self.password_entry, False, False, 6)

        self.unlock_button.set_label(_("Unlock"))
        self.unlock_button.connect("clicked", self.on_unlock)

        password_box.pack_start(self.unlock_button, False, False, 6)
        self.pack_start(password_box, True, False, 6)

    def on_unlock(self, *args):
        """
            Password check and unlock
        """
        typed_pass = self.password_entry.get_text()
        ecrypted_pass = sha256(typed_pass.encode("utf-8")).hexdigest()
        login_pass = self.app.cfg.read("password", "login")
        if ecrypted_pass == login_pass or login_pass == typed_pass:
            self.password_entry.set_icon_from_icon_name(
                Gtk.EntryIconPosition.SECONDARY, None)
            self.toggle_lock()
            self.password_entry.set_text("")
        else:
            self.password_entry.set_icon_from_icon_name(
                Gtk.EntryIconPosition.SECONDARY, "dialog-error-symbolic")

    def toggle_lock(self):
        """
            Lock/unlock the application
        """
        self.app.locked = not self.app.locked
        if self.app.locked:
            self.focus()
        self.app.refresh_menu()
        self.app.win.refresh_window()

    def toggle(self, visible):
        self.set_visible(visible)
        self.set_no_show_all(not visible)

    def hide(self):
        self.toggle(False)

    def show(self):
        self.toggle(True)

    def focus(self):
        self.password_entry.grab_focus_without_selecting()
