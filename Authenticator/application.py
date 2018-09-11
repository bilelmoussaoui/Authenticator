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
from gi.repository import Gtk, GLib, Gio, Gdk
from .widgets import Window, AboutDialog, import_json, export_json, import_pgp_json, export_pgp_json
from .models import Settings, Clipboard, Logger


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

    def do_startup(self):
        """Startup the application."""
        Gtk.Application.do_startup(self)
        # Unlock the keyring
        self.__generate_menu()
        self.__setup_actions()
        Application.__setup_css()

        # Set the default night mode
        is_night_mode = Settings.get_default().is_night_mode
        gtk_settings = Gtk.Settings.get_default()
        gtk_settings.set_property("gtk-application-prefer-dark-theme",
                                  is_night_mode)

    @staticmethod
    def __setup_css():
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

    def __generate_menu(self):
        """Generate application menu."""
        # Backup
        backup_content = Gio.Menu.new()
        import_menu = Gio.Menu.new()
        export_menu = Gio.Menu.new()

        import_menu.append_item(Gio.MenuItem.new(_("from a plain-text JSON file"), "app.import_json"))
        import_menu.append_item(Gio.MenuItem.new(_("from an OpenPGP-encrypted JSON file"), "app.import_pgp_json"))
        export_menu.append_item(Gio.MenuItem.new(_("in a plain-text JSON file"), "app.export_json"))
        export_menu.append_item(Gio.MenuItem.new(_("in an OpenPGP-encrypted JSON file"), "app.export_pgp_json"))

        backup_content.insert_submenu(0, _("Restore"), import_menu)
        backup_content.insert_submenu(1, _("Backup"), export_menu)

        backup_section = Gio.MenuItem.new_section(None, backup_content)
        self._menu.append_item(backup_section)

        # Main section
        main_content = Gio.Menu.new()
        # Night mode action
        main_content.append_item(Gio.MenuItem.new(_("Settings"), "app.settings"))
        main_content.append_item(Gio.MenuItem.new(_("About"), "app.about"))
        main_content.append_item(Gio.MenuItem.new(_("Quit"), "app.quit"))
        help_section = Gio.MenuItem.new_section(None, main_content)
        self._menu.append_item(help_section)

    def __setup_actions(self):
        settings = Settings.get_default()

        actions = {
            "about": self.__on_about,
            "quit": self.__on_quit,
            "settings": self.__on_settings,
            "import_json": self.__on_import_json,
            "import_pgp_json": self.__on_import_pgp_json,
            "export_json": self.__on_export_json,
            "export_pgp_json": self.__on_export_pgp_json
        }
        for key, value in actions.items():
            action = Gio.SimpleAction.new(key, None)
            action.connect("activate", value)
            self.add_action(action)

    def do_activate(self, *_):
        """On activate signal override."""
        resources_path = "/com/github/bilelmoussaoui/Authenticator/"
        Gtk.IconTheme.get_default().add_resource_path(resources_path)
        window = Window.get_default()
        window.set_application(self)
        window.set_menu(self._menu)
        window.connect("delete-event", lambda x, y: self.__on_quit())
        self.add_window(window)
        window.show_all()
        window.present()

    @staticmethod
    def set_use_qrscanner(state):
        Application.USE_QRSCANNER = state

    @staticmethod
    def __on_about(*_):
        """
            Shows about dialog
        """
        dialog = AboutDialog()
        dialog.set_transient_for(Window.get_default())
        dialog.run()
        dialog.destroy()

    @staticmethod
    def __on_import_json(*_):
        from .models import BackupJSON
        filename = import_json(Window.get_default())
        if filename:
            BackupJSON.import_file(filename)
        Window.get_default().update_view()

    @staticmethod
    def __on_export_json(*_):
        from .models import BackupJSON
        filename = export_json(Window.get_default())
        if filename:
            BackupJSON.export_file(filename)

    @staticmethod
    def __on_import_pgp_json(*_):
        from .widgets import GPGRestoreWindow
        filename = import_pgp_json(Window.get_default())
        if filename:
            gpg_window = GPGRestoreWindow(filename)
            gpg_window.set_transient_for(Window.get_default())
            gpg_window.show_all()

    @staticmethod
    def __on_export_pgp_json(*_):
        from .models import BackupPGPJSON
        filename = export_pgp_json(Window.get_default())
        if filename:
            def export_pgp(_, fingerprint):
                BackupPGPJSON.export_file(filename, fingerprint)

            from .widgets.backup import FingprintPGPWindow
            fingerprint_window = FingprintPGPWindow(filename)
            fingerprint_window.set_transient_for(Window.get_default())
            fingerprint_window.connect("selected", export_pgp)
            fingerprint_window.show_all()

    @staticmethod
    def __on_settings(*_):
        from .widgets import SettingsWindow
        settings_window = SettingsWindow()
        settings_window.present()
        settings_window.show_all()

    def __on_quit(self, *_):
        """
        Close the application, stops all threads
        and clear clipboard for safety reasons
        """
        Clipboard.clear()
        Window.get_default().close()
        self.quit()
