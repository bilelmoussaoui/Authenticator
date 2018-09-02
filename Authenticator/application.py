"""
 Copyright © 2017 Bilal Elmoussaoui <bil.elmoussaoui@gmail.com>

 This file is part of Authenticator.

 Authenticator is free software: you can redistribute it and/or
 modify it under the terms of the GNU General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 Authenticator is distr  ibuted in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Authenticator. If not, see <http://www.gnu.org/licenses/>.
"""
from gettext import gettext as _

from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gio, Gdk, GObject
from .widgets import Window, AboutDialog
from .models import Settings, Keyring, Clipboard, Logger


class Application(Gtk.Application):
    """Authenticator application object."""
    instance = None
    USE_QRSCANNER = True

    def __init__(self):
        Gtk.Application.__init__(self,
                                 application_id="com.github.bilelmoussaoui.Authenticator",
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)
        GLib.set_application_name(_("Authenticator"))
        GLib.set_prgname("Authenticator")
        self.alive = True
        self._menu = Gio.Menu()

    @staticmethod
    def get_default():
        if Application.instance is None:
            Application.instance = Application()
        return Application.instance

    def setup_css(self):
        """Setup the CSS and load it."""
        uri = 'resource:///com/github/bilelmoussaoui/Authenticator/style.css'
        provider_file = Gio.File.new_for_uri(uri)
        provider = Gtk.CssProvider()
        screen = Gdk.Screen.get_default()
        context = Gtk.StyleContext()
        provider.load_from_file(provider_file)
        context.add_provider_for_screen(screen, provider,
                                        Gtk.STYLE_PROVIDER_PRIORITY_USER)
        Logger.debug("Loading CSS")

    def do_startup(self):
        """Startup the application."""
        Gtk.Application.do_startup(self)
        # Unlock the keyring
        self.generate_menu()
        self.setup_css()

        # Set the default night mode
        is_night_mode = Settings.get_default().is_night_mode
        gtk_settings = Gtk.Settings.get_default()
        gtk_settings.set_property("gtk-application-prefer-dark-theme",
                                  is_night_mode)

    def generate_menu(self):
        """Generate application menu."""
        settings = Settings.get_default()

        # Help section
        help_content = Gio.Menu.new()
        # Night mode action
        help_content.append_item(Gio.MenuItem.new(_("Night Mode"),
                                                  "app.night_mode"))

        help_content.append_item(Gio.MenuItem.new(_("About"), "app.about"))
        help_content.append_item(Gio.MenuItem.new(_("Quit"), "app.quit"))
        help_section = Gio.MenuItem.new_section(None, help_content)
        self._menu.append_item(help_section)

        is_night_mode = settings.is_night_mode
        gv_is_night_mode = GLib.Variant.new_boolean(is_night_mode)
        action = Gio.SimpleAction.new_stateful("night_mode", None,
                                               gv_is_night_mode)
        action.connect("change-state", self.on_night_mode)
        self.add_action(action)

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)

    def do_activate(self, *args):
        """On activate signal override."""
        resources_path = "/com/github/bilelmoussaoui/Authenticator/"
        Gtk.IconTheme.get_default().add_resource_path(resources_path)
        window = Window.get_default()
        window.set_application(self)
        window.set_menu(self._menu)
        window.connect("delete-event", lambda x, y: self.on_quit())
        self.add_window(window)
        window.show_all()
        window.present()

    def set_use_qrscanner(self, state):
        Application.USE_QRSCANNER = state

    def on_night_mode(self, action, *args):
        """Switch night mode."""
        settings = Settings.get_default()
        is_night_mode = not settings.is_night_mode
        action.set_state(GLib.Variant.new_boolean(is_night_mode))
        settings.is_night_mode = is_night_mode
        gtk_settings = Gtk.Settings.get_default()
        gtk_settings.set_property("gtk-application-prefer-dark-theme",
                                  is_night_mode)

    def on_about(self, *args):
        """
            Shows about dialog
        """
        dialog = AboutDialog()
        dialog.set_transient_for(Window.get_default())
        dialog.run()
        dialog.destroy()

    def on_settings(self, *args):
        """
            Shows settings window
        """
        settings_window = SettingsWindow()
        settings_window.set_attached_to(Window.get_default())
        settings_window.show_window()

    def on_quit(self, *args):
        """
        Close the application, stops all threads
        and clear clipboard for safety reasons
        """
        Clipboard.clear()
        from .widgets.accounts.list import AccountsList
        accounts = AccountsList.get_default()
        for account_row in accounts:
            account_row.account.kill()

        window = Window.get_default()
        window.save_state()
        window.destroy()
        self.quit()
