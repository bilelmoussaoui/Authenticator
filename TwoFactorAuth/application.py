#!/usr/bin/env python3
from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gio, Gdk, GObject
from TwoFactorAuth.widgets.window import Window
from TwoFactorAuth.models.authenticator import Authenticator
from TwoFactorAuth.widgets.settings import SettingsWindow
from TwoFactorAuth.models.settings import SettingsReader
import logging
import signal
from gettext import gettext as _


class Application(Gtk.Application):
    win = None
    alive = True
    locked = False
    menu = Gio.Menu()
    auth = Authenticator()

    def __init__(self, *args, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])
        Gtk.Application.__init__(self,
                                 application_id='org.gnome.TwoFactorAuth',
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)
        GLib.set_application_name("TwoFactorAuth")
        GLib.set_prgname(self.package)
        self.cfg = SettingsReader()
        if self.cfg.read("state", "login"):
            self.locked = True
        GObject.threads_init()
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
        if self.locked:
            self.menu.append(_("Unlock the Application"), "app.lock")
        else:
            self.menu.append(_("Lock the Application"), "app.lock")

        self.menu.append(_("Settings"), "app.settings")
        if Gtk.get_major_version() >= 3 and Gtk.get_minor_version() >= 20:
            self.menu.append(_("Shortcuts"), "app.shortcuts")
        self.menu.append(_("About"), "app.about")
        self.menu.append(_("Quit"), "app.quit")
        self.set_app_menu(self.menu)

        action = Gio.SimpleAction.new("settings", None)
        action.connect("activate", self.on_settings)
        self.add_action(action)

        if Gtk.get_major_version() >= 3 and Gtk.get_minor_version() >= 20:
            action = Gio.SimpleAction.new("shortcuts", None)
            action.connect("activate", self.on_shortcuts)
            self.add_action(action)

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)

        action = Gio.SimpleAction.new("lock", None)
        action.connect("activate", self.on_toggle_lock)
        self.add_action(action)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)

        self.toggle_settings_menu()
        logging.debug("Adding gnome shell menu")

    def do_activate(self, *args):
        self.win = Window(self)
        self.win.show_all()
        self.add_window(self.win)

    def toggle_settings_menu(self):
        if self.locked:
            self.menu.remove(1)
        else:
            self.menu.insert(1, _("Settings"), "app.settings")

    def on_toggle_lock(self, *args):
        if not self.locked:
            self.locked = not self.locked
            self.toggle_app_lock_menu()
            self.toggle_settings_menu()
            self.win.refresh_window()

    def toggle_app_lock_menu(self):
        if self.locked:
            label = _("Unlock the Application")
        else:
            label = _("Lock the Application")
        self.menu.remove(0)
        self.menu.insert(0, label, "app.lock")

    def on_shortcuts(self, *args):
        self.win.show_shortcuts()

    def on_about(self, *args):
        self.win.show_about()

    def on_settings(self, *args):
        """
            Shows settings window
        """
        SettingsWindow(self.win)

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
        self.win.destroy()
        self.quit()
