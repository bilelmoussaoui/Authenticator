from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, Gdk, GObject, GLib
from TwoFactorAuth.widgets.add_account import AddAccount
from TwoFactorAuth.widgets.accounts_window import AccountsWindow
from TwoFactorAuth.widgets.login_window import LoginWindow
from TwoFactorAuth.widgets.no_account_window import NoAccountWindow
from TwoFactorAuth.widgets.headerbar import HeaderBar
import logging
from hashlib import sha256
from gettext import gettext as _


class Window(Gtk.ApplicationWindow):
    counter = 0
    main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    is_select_mode = False

    def __init__(self, application):
        self.app = application
        self.generate_window()
        self.generate_header_bar()
        self.generate_accounts_box()
        self.generate_no_accounts_box()
        self.generate_login_box()
        self.refresh_window()
        GLib.timeout_add_seconds(60, self.refresh_counter)

    def generate_window(self, *args):
        """
            Generate application window (Gtk.Window)
        """
        Gtk.ApplicationWindow.__init__(self, type=Gtk.WindowType.TOPLEVEL,
                                       application=self.app)
        self.move_latest_position()
        self.set_wmclass("Gnome-TwoFactorAuth", "Gnome TwoFactorAuth")
        self.set_icon_name("Gnome-TwoFactorAuth")
        self.resize(420, 550)
        self.set_size_request(420, 550)
        self.set_resizable(False)
        self.connect("key_press_event", self.on_key_press)
        self.connect("delete-event", lambda x, y: self.app.on_quit())
        self.add(self.main_box)

    def on_key_press(self, app, key_event):
        """
            Keyboard Listener handling
        """
        keyname = Gdk.keyval_name(key_event.keyval).lower()
        if not self.is_locked():

            if not self.no_account_box.is_visible():
                if keyname == "s" or keyname == "escape":
                    if key_event.state == Gdk.ModifierType.CONTROL_MASK or not self.hb.select_button.get_visible():
                        self.toggle_select()
                        return True

            if keyname == "n":
                if key_event.state == Gdk.ModifierType.CONTROL_MASK:
                    self.add_account()
                    return True

        return False

    def refresh_counter(self):
        """
            Add a value to the counter each 60 seconds
        """
        if not self.app.locked:
            self.counter += 1
        if self.app.cfg.read("auto-lock", "preferences"):
            if self.counter == self.app.cfg.read("auto-lock-time", "preferences") - 1:
                self.counter = 0
                self.toggle_lock()
        return True

    def generate_login_box(self):
        """
            Generate login form
        """
        self.login_box = LoginWindow(self.app, self)
        self.hb.lock_button.connect("clicked", self.login_box.toggle_lock)
        self.main_box.pack_start(self.login_box, True, False, 0)

    def generate_accounts_box(self):
        self.accounts_box = AccountsWindow(self.app, self)
        self.accounts_list = self.accounts_box.get_accounts_list()
        self.hb.remove_button.connect("clicked", self.accounts_list.remove_selected)
        self.search_bar = self.accounts_box.get_search_bar()
        self.main_box.pack_start(self.accounts_box, True, True, 0)

    def generate_header_bar(self):
        """
            Generate a header bar box
        """
        self.hb = HeaderBar(self.app, self)
        # connect signals
        self.hb.cancel_button.connect("clicked", self.toggle_select)
        self.hb.select_button.connect("clicked", self.toggle_select)
        self.hb.add_button.connect("clicked", self.add_account)
        self.set_titlebar(self.hb)

    def add_account(self, *args):
        """
            Create add application window
        """
        add_account = AddAccount(self)
        add_account.show_window()

    def toggle_select(self, *args):
        """
            Toggle select mode
        """
        self.is_select_mode = not self.is_select_mode
        self.hb.toggle_select_mode()
        self.accounts_list.toggle_select_mode()

    def generate_no_accounts_box(self):
        """
            Generate a box with no accounts message
        """
        self.no_account_box = NoAccountWindow()
        self.main_box.pack_start(self.no_account_box, True, False, 0)

    def refresh_window(self):
        """
            Refresh windows components
        """
        count = self.app.db.count()
        if self.is_locked():
            self.login_box.show()
            self.no_account_box.hide()
            self.accounts_box.hide()
        else:
            self.login_box.hide()
            if count == 0:
                self.no_account_box.show()
                self.accounts_box.hide()
            else:
                self.accounts_box.show()
                self.no_account_box.hide()
        self.hb.refresh()
        self.main_box.show_all()

    def is_locked(self):
        return self.app.locked

    def save_window_state(self):
        """
            Save window position
        """
        x, y = self.get_position()
        self.app.cfg.update("position-x", x, "preferences")
        self.app.cfg.update("position-y", y, "preferences")

    def move_latest_position(self):
        """
            move the application window to the latest position
        """
        x = self.app.cfg.read("position-x", "preferences")
        y = self.app.cfg.read("position-y", "preferences")
        if x != 0 and y != 0:
            self.move(x, y)
        else:
            self.set_position(Gtk.WindowPosition.CENTER)
