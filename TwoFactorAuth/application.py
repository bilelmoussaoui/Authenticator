#!/usr/bin/env python3
from gi import require_version
require_version("Gtk", "3.0")
require_version("GnomeKeyring", "1.0")
from gi.repository import Gtk, GLib, Gio, Gdk, GObject, GnomeKeyring as GK
from TwoFactorAuth.widgets.window import Window
from TwoFactorAuth.models.authenticator import Authenticator
from TwoFactorAuth.widgets.settings import SettingsWindow
from TwoFactorAuth.models.settings import SettingsReader
import logging
import signal
from gettext import gettext as _
from os import environ as env


class Application(Gtk.Application):
    win = None
    alive = True
    locked = False
    menu = Gio.Menu()
    auth = Authenticator()
    use_GMenu = True

    settings_window = None
    settings_action = None

    def __init__(self, *args, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])
        Gtk.Application.__init__(self,
                                 application_id='org.gnome.TwoFactorAuth',
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)
        GLib.set_application_name("TwoFactorAuth")
        GLib.set_prgname(self.package)
        current_desktop = env.get("XDG_CURRENT_DESKTOP")
        if current_desktop:
            self.use_GMenu = current_desktop.lower() == "gnome"
        else:
            self.use_GMenu = False

        result = GK.unlock_sync("TwoFactorAuth", None)
        if result == GK.Result.CANCELLED:
            self.quit()

        self.cfg = SettingsReader()
        if self.cfg.read("state", "login"):
            self.locked = True
        provider = Gtk.CssProvider()
        css_file = self.pkgdatadir + "/data/style.css"
        try:
            provider.load_from_path(css_file)
            Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),
                                                     provider,
                                                     Gtk.STYLE_PROVIDER_PRIORITY_USER)
            logging.debug("Loading css file %s" % css_file)
        except Exception as e:
            logging.debug("File not found %s" % css_file)
            logging.debug("Error message %s" % str(e))

    def do_startup(self):
        Gtk.Application.do_startup(self)
        if self.use_GMenu:
            self.generate_menu()
            logging.debug("Adding gnome shell menu")

    def generate_menu(self):
        # Settings section
        settings_content = Gio.Menu.new()
        settings_content.append_item(Gio.MenuItem.new(_("Settings"), "app.settings"))
        settings_section = Gio.MenuItem.new_section(None, settings_content)
        self.menu.append_item(settings_section)

        # Help section
        help_content = Gio.Menu.new()
        if Gtk.get_major_version() >= 3 and Gtk.get_minor_version() >= 20:
            help_content.append_item(Gio.MenuItem.new(_("Shortcuts"), "app.shortcuts"))

        help_content.append_item(Gio.MenuItem.new(_("About"), "app.about"))
        help_content.append_item(Gio.MenuItem.new(_("Quit"), "app.quit"))
        help_section = Gio.MenuItem.new_section(None, help_content)
        self.menu.append_item(help_section)

        self.set_app_menu(self.menu)

        self.settings_action = Gio.SimpleAction.new("settings", None)
        self.settings_action.connect("activate", self.on_settings)
        self.settings_action.set_enabled(not self.locked)
        self.add_action(self.settings_action)

        if Gtk.get_major_version() >= 3 and Gtk.get_minor_version() >= 20:
            action = Gio.SimpleAction.new("shortcuts", None)
            action.connect("activate", self.on_shortcuts)
            self.add_action(action)

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)

    def do_activate(self, *args):
        self.win = Window(self)
        self.win.show_all()
        self.add_window(self.win)

    def refresh_menu(self):
        if self.use_GMenu:
            self.settings_action.set_enabled(not self.settings_action.get_enabled())

    def on_toggle_lock(self, *args):
        if not self.locked:
            self.locked = not self.locked
            self.win.password_entry.grab_focus_without_selecting()
            self.refresh_menu()
            self.win.refresh_window()

    def on_shortcuts(self, *args):
        self.win.show_shortcuts()

    def on_about(self, *args):
        self.win.show_about()

    def on_settings(self, *args):
        """
            Shows settings window
        """
        try:
            settings_window = SettingsWindow(self.win)
            settings_window.show_window()
        except Exception as e:
            print(e)
              
    def on_quit(self, *args):
        """
        Close the application, stops all threads
        and clear clipboard for safety reasons
        """
        try:
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            clipboard.clear()
        except Exception as e:
            logging.error(str(e))
        self.alive = False
        signal.signal(signal.SIGINT, lambda x, y: self.alive)
        if self.win:
            self.win.destroy()
        self.quit()
