"""
 Copyright © 2017 Bilal Elmoussaoui <bil.elmoussaoui@gmail.com>

 This file is part of Gnome Authenticator.

 Gnome Authenticator is free software: you can redistribute it and/or
 modify it under the terms of the GNU General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 TwoFactorAuth is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Gnome Authenticator. If not, see <http://www.gnu.org/licenses/>.
"""
from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, Gdk, GObject, GLib
from ..models import Logger, Settings
from .headerbar import HeaderBar
from .inapp_notification import InAppNotification
from .accounts import AccountsList


class Window(Gtk.ApplicationWindow, GObject.GObject):
    """Main Window object."""
    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_LAST, None, (bool,))
    }
    counter = 1
    is_select_mode = False

    # Default Window instance
    instance = None

    def __init__(self):
        Gtk.ApplicationWindow.__init__(self, type=Gtk.WindowType.TOPLEVEL)
        self.set_wmclass("org.gnome.Authenticator", "Gnome Authenticator")
        self.set_icon_name("org.gnome.Authenticator")
        self.set_resizable(True)
        self.restore_state()
        self._build_widgets()
        #self.connect("key_press_event", self.on_key_press)

        self.show_all()
        Settings.get_default().connect("changed", self.bind_view)
        GLib.timeout_add_seconds(60, self.refresh_counter)

    @staticmethod
    def get_default():
        """Return the default instance of Window."""
        if Window.instance is None:
            Window.instance = Window()
        return Window.instance

    def bind_view(self, settings, key):
        if key == "locked":
            count = self.app.db.count()
            is_locked = settings.get_is_locked()
            self.accounts_box.set_visible(not is_locked and count != 0)
            self.accounts_box.set_no_show_all(
                not (not is_locked and count != 0))
            self.no_account_box.set_visible(not is_locked and count == 0)
            self.no_account_box.set_no_show_all(
                not(not is_locked and count == 0))
            self.show_all()

    def on_key_press(self, app, key_event):
        """
            Keyboard Listener handling
        """
        keyname = Gdk.keyval_name(key_event.keyval).lower()
        if not Settings.get_default().is_locked:
            if not self.no_account_box.is_visible():
                if keyname == "s" or keyname == "escape":
                    if key_event.state == Gdk.ModifierType.CONTROL_MASK or not self.hb.select_button.get_visible():
                        self.toggle_select()
                        return True

            if keyname == "n":
                if key_event.state == Gdk.ModifierType.CONTROL_MASK:
                    self.add_account()
                    return True
            if keyname == "m":
                if key_event.state == Gdk.ModifierType.CONTROL_MASK:
                    self.hb.toggle_view_mode()
                    return True
        return False

    def refresh_counter(self):
        """
            Add a value to the counter each 60 seconds
        """
        settings = Settings.get_default()
        if settings.auto_lock and not settings.is_locked:
            self.counter += 1
            if self.counter == settings.auto_lock_time:
                self.counter = 1
                self.emit("locked", True)
        return True

    def _build_widgets(self):
        """Build main window widgets."""
        # HeaderBar
        headerbar = HeaderBar.get_default()
        # connect signals
        headerbar.select_btn.connect("clicked", self.toggle_select)
        headerbar.add_btn.connect("clicked", self.add_account)
        self.set_titlebar(headerbar)

        # Main Container
        self.main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # In App Notifications
        # TODO: replace this with the gtk4 implementation
        self.notification = InAppNotification()
        self.main_container.pack_start(self.notification, False, False, 0)

        # Accounts List
        self.main_container.pack_start(
            AccountsList.get_default(), False, False, 0)

        self.add(self.main_container)

    def add_account(self, *args):
        print(args)

    def toggle_select(self, *args):
        """
            Toggle select mode
        """
        self.is_select_mode = not self.is_select_mode
        self.hb.toggle_select_mode()
        self.accounts_list.toggle_select_mode()

    def save_state(self):
        """Save window position & size."""
        settings = Settings.get_default()
        settings.window_position = self.get_position()
        settings.window_size = self.get_size()

    def restore_state(self):
        """Restore the window's state."""
        settings = Settings.get_default()
        # Restore the window position
        position_x, position_y = settings.window_position
        if position_x != 0 and position_y != 0:
            self.move(position_x, position_y)
            Logger.debug("[Window] Restore postion x: {}, y: {}".format(position_x,
                                                                        position_y))
        else:
            # Fallback to the center
            self.set_position(Gtk.WindowPosition.CENTER)
        # Restore window's size
        width, height = settings.window_size
        default_width, default_height = settings.default_size
        Logger.debug("[Window] Restore size width: {}, height: {}".format(width,
                                                                          height))
        self.resize(width, height)
        self.set_size_request(default_width, default_height)
