#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 Copyright © 2016 Bilal Elmoussaoui <bil.elmoussaoui@gmail.com>

 This file is part of Gnome-TwoFactorAuth.

 Gnome-TwoFactorAuth is free software: you can redistribute it and/or
 modify it under the terms of the GNU General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 TwoFactorAuth is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Gnome-TwoFactorAuth. If not, see <http://www.gnu.org/licenses/>.
"""
from gi import require_version
require_version("Gtk", "3.0")
require_version("GnomeKeyring", "1.0")
from gi.repository import Gtk, GLib, Gio, Gdk, GObject, GnomeKeyring as GK
from TwoFactorAuth.widgets.window import Window
from TwoFactorAuth.models.database import Database
from TwoFactorAuth.widgets.settings import SettingsWindow
from TwoFactorAuth.models.settings import SettingsReader
from TwoFactorAuth.utils import *
import logging
import signal
from gettext import gettext as _
from os import environ as env

class Application(Gtk.Application):
    win = None
    alive = True
    locked = False

    settings_action = None

    def __init__(self):
        Gtk.Application.__init__(self,
                                 application_id="org.gnome.TwoFactorAuth",
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)
        GLib.set_application_name(_("TwoFactorAuth"))
        GLib.set_prgname("Gnome-TwoFactorAuth")

        self.menu = Gio.Menu()
        self.db = Database()
        self.cfg = SettingsReader()
        self.locked = self.cfg.read("state", "login")

        result = GK.unlock_sync("Gnome-TwoFactorAuth", None)
        if result == GK.Result.CANCELLED:
            self.quit()

        if Gtk.get_major_version() >= 3 and Gtk.get_minor_version() >= 20:
            cssFileName = "gnome-twofactorauth-post3.20.css"
        else:
            cssFileName = "ggnome-twofactorauth-pre3.20.css"
        cssProviderFile = Gio.File.new_for_uri('resource:///org/gnome/TwoFactorAuth/%s' % cssFileName)
        cssProvider = Gtk.CssProvider()
        screen = Gdk.Screen.get_default()
        styleContext = Gtk.StyleContext()
        try:
            cssProvider.load_from_file(cssProviderFile)
            styleContext.add_provider_for_screen(screen, cssProvider,
                                             Gtk.STYLE_PROVIDER_PRIORITY_USER)
            logging.debug("Loading css file ")
        except Exception as e:
            logging.error("Error message %s" % str(e))

    def do_startup(self):
        Gtk.Application.do_startup(self)
        self.generate_menu()

    def generate_menu(self):
        # Settings section
        settings_content = Gio.Menu.new()
        settings_content.append_item(
            Gio.MenuItem.new(_("Settings"), "app.settings"))
        settings_section = Gio.MenuItem.new_section(None, settings_content)
        self.menu.append_item(settings_section)

        # Help section
        help_content = Gio.Menu.new()
        if Gtk.get_major_version() >= 3 and Gtk.get_minor_version() >= 20:
            help_content.append_item(Gio.MenuItem.new(
                _("Shortcuts"), "app.shortcuts"))

        help_content.append_item(Gio.MenuItem.new(_("About"), "app.about"))
        help_content.append_item(Gio.MenuItem.new(_("Quit"), "app.quit"))
        help_section = Gio.MenuItem.new_section(None, help_content)
        self.menu.append_item(help_section)

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

        if is_gnome():
            self.set_app_menu(self.menu)
            logging.debug("Adding gnome shell menu")

    def do_activate(self, *args):
        if not self.win:
            self.win = Window(self)
            self.win.show_all()
            self.add_window(self.win)
        else:
            self.win.present()

    def refresh_menu(self):
        is_enabled = self.settings_action.get_enabled()
        self.settings_action.set_enabled(not is_enabled)

    def on_shortcuts(self, *args):
        """
            Shows keyboard shortcuts
        """
        shortcuts = Application.shortcuts_dialog()
        if shortcuts:
            shortcuts.set_transient_for(self.win)
            shortcuts.show()

    @staticmethod
    def shortcuts_dialog():
        if Gtk.get_major_version() >= 3 and Gtk.get_minor_version() >= 20:
            builder = Gtk.Builder()
            builder.add_from_resource('/org/gnome/TwoFactorAuth/shortcuts.ui')
            shortcuts = builder.get_object("shortcuts")
            return shortcuts
        return None

    @staticmethod
    def about_dialog():
        """
            Shows about dialog
        """
        builder = Gtk.Builder()
        builder.add_from_resource('/org/gnome/TwoFactorAuth/about.ui')

        dialog = builder.get_object("AboutDialog")
        return dialog

    def on_about(self, *args):
        """
            Shows about dialog
        """
        dialog = Application.about_dialog()
        dialog.set_transient_for(self.win)
        dialog.run()
        dialog.destroy()

    def on_settings(self, *args):
        """
            Shows settings window
        """
        settings_window = SettingsWindow(self.win)
        settings_window.show_window()
        settings_window.present()

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
            self.win.save_window_state()
            self.win.destroy()
        self.quit()
