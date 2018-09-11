"""
 Copyright © 2017 Bilal Elmoussaoui <bil.elmoussaoui@gmail.com>

 This file is part of Authenticator.

 Authenticator is free software: you can redistribute it and/or
 modify it under the terms of the GNU General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 Authenticator is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Authenticator. If not, see <http://www.gnu.org/licenses/>.
"""

from gettext import gettext as _

from gi import require_version

require_version('Gd', '1.0')
require_version("Gtk", "3.0")
from gi.repository import Gd, Gtk, GObject
from .window import Window
from ..models import Settings


class ClickableSettingsBox(Gtk.EventBox):

    def __init__(self, label, sub_label=None):
        Gtk.EventBox.__init__(self)

        # cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
        # self.get_window().set_cursor(cursor)
        self._build_widgets(label, sub_label)

    def _build_widgets(self, label, sub_label=None):
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        container.get_style_context().add_class("settings-box")

        main_lbl = Gtk.Label()
        main_lbl.set_halign(Gtk.Align.START)
        main_lbl.get_style_context().add_class("settings-box-main-label")
        main_lbl.set_text(label)
        container.pack_start(main_lbl, True, True, 3)
        self.secondary_lbl = Gtk.Label()
        self.secondary_lbl.set_halign(Gtk.Align.START)
        self.secondary_lbl.get_style_context().add_class("settings-box-secondary-label")
        if sub_label:
            self.secondary_lbl.set_text(sub_label)
        else:
            self.secondary_lbl.set_text("")
        container.pack_start(self.secondary_lbl, True, True, 3)

        self.add(container)


class SwitchSettingsBox(Gtk.Box, GObject.GObject):
    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_LAST, None, (bool,))
    }

    def __init__(self, label, sub_label, schema):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        GObject.GObject.__init__(self)
        self.switch = Gtk.Switch()
        self._schema = schema
        self._build_widgets(label, sub_label)

    def _build_widgets(self, label, sub_label):
        self.get_style_context().add_class("settings-box")

        self.switch.set_state(Settings.get_default().get_boolean(self._schema))
        self.switch.connect("state-set", self.__on_toggled)

        label_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_lbl = Gtk.Label()
        main_lbl.set_halign(Gtk.Align.START)
        main_lbl.get_style_context().add_class("settings-box-main-label")
        main_lbl.set_text(label)
        label_container.pack_start(main_lbl, False, False, 3)
        secondary_lbl = Gtk.Label()
        secondary_lbl.set_halign(Gtk.Align.START)
        secondary_lbl.get_style_context().add_class("settings-box-secondary-label")
        secondary_lbl.set_text(sub_label)
        label_container.pack_start(secondary_lbl, False, False, 3)

        self.pack_start(label_container, False, False, 0)

        switch_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        switch_container.pack_start(self.switch, False, False, 0)
        switch_container.set_valign(Gtk.Align.CENTER)
        self.pack_end(switch_container, False, False, 0)

    def __on_toggled(self, *_):
        Settings.get_default().set_boolean(self._schema, not self.switch.get_state())
        self.emit("changed", not self.switch.get_state())


class SettingsBoxWithEntry(Gtk.Box):

    def __init__(self, label, is_password=False):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        self.get_style_context().add_class("settings-box")
        self.entry = Gtk.Entry()
        if is_password:
            self.entry.set_visibility(False)
        self._build_widgets(label)

    def _build_widgets(self, label):
        entry_label = Gtk.Label()
        entry_label.set_text(label)
        entry_label.get_style_context().add_class("settings-box-main-label")
        entry_label.set_halign(Gtk.Align.START)

        self.pack_start(entry_label, True, True, 6)
        self.pack_end(self.entry, False, False, 6)


class PasswordWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_modal(True)
        self.set_size_request(500, 400)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.resize(500, 400)
        self.set_resizable(False)
        self.set_border_width(36)
        self.old_password = None
        self._apply_btn = Gtk.Button()
        self._build_widgets()

    def _build_widgets(self):
        header_bar = Gtk.HeaderBar()
        header_bar.set_title(_("Backup Password"))
        header_bar.set_show_close_button(True)
        self.set_titlebar(header_bar)

        self._apply_btn.set_label(_("Save"))
        self._apply_btn.connect("clicked", self.__on_apply_button_clicked)
        self._apply_btn.set_sensitive(False)
        self._apply_btn.get_style_context().add_class("suggested-action")

        header_bar.pack_end(self._apply_btn)

        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        if Settings.get_default().backup_password:
            self.old_password = SettingsBoxWithEntry(_("Old Password"), True)
            self.old_password.entry.connect("changed", self._validate)
            container.pack_start(self.old_password, False, False, 6)

        self.password = SettingsBoxWithEntry(_("Password"), True)
        self.password.entry.connect("changed", self._validate)

        self.repeat_password = SettingsBoxWithEntry(_("Repeat Password"), True)
        self.repeat_password.entry.connect("changed", self._validate)

        container.pack_start(self.password, False, False, 6)
        container.pack_start(self.repeat_password, False, False, 6)

        self.add(container)

    def _validate(self, *_):
        password = self.password.entry.get_text()
        repeat_password = self.repeat_password.entry.get_text()
        if not password:
            self.password.entry.get_style_context().add_class("error")
            valid_password = False
        else:
            self.password.entry.get_style_context().remove_class("error")
            valid_password = True

        if not repeat_password or password != repeat_password:
            self.repeat_password.entry.get_style_context().add_class("error")
            valid_repeat_password = False
        else:
            self.repeat_password.entry.get_style_context().remove_class("error")
            valid_repeat_password = True

        to_validate = [valid_password, valid_repeat_password]

        if self.old_password:
            old_password = self.old_password.entry.get_text()
            if not old_password or old_password != Settings.get_default().backup_password:
                self.old_password.entry.get_style_context().add_class("error")
                valid_old_password = False
            else:
                self.old_password.entry.get_style_context().remove_class("error")
                valid_old_password = True
            to_validate.append(valid_old_password)

        self._apply_btn.set_sensitive(all(to_validate))

    def __on_apply_button_clicked(self, *_):
        if self._apply_btn.get_sensitive():
            password = self.password.entry.get_text()
            Settings.get_default().backup_password = password
            self.destroy()


class SettingsWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_transient_for(Window.get_default())
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_size_request(600, 600)
        self.set_title(_("Settings"))
        self.resize(600, 600)

        self.stack_switcher = Gtk.StackSwitcher()
        self.stack = Gtk.Stack()

        self._build_widgets()

    def _build_widgets(self):
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_close_button(True)
        self.set_titlebar(header_bar)
        header_bar.set_custom_title(self.stack_switcher)
        self.stack_switcher.set_stack(self.stack)
        self.stack.get_style_context().add_class("settings-main-container")

        appearance_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        dark_theme = SwitchSettingsBox(_("Dark theme"), _("Use a dark theme, if possible"), "night-mode")
        dark_theme.connect("changed", self.__on_dark_theme_changed)
        appearance_container.pack_start(dark_theme, False, False, 0)
        self.stack.add_titled(appearance_container, "appearance", _("Appearance"))

        behaviour_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        clear_database = ClickableSettingsBox(_("Clear the database"), _("Erase existing accounts"))
        clear_database.connect("button-press-event", self.__on_clear_database_clicked)
        behaviour_container.pack_start(clear_database, False, False, 0)
        self.stack.add_titled(behaviour_container, "behaviour", _("Behaviour"))

        backup_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        gpg_location = ClickableSettingsBox(_("GPG keys location"),
                                            Settings.get_default().gpg_location)
        gpg_location.connect("button-press-event", self.__on_gpg_location_clicked)

        backup_container.pack_start(gpg_location, False, False, 0)
        self.stack.add_titled(backup_container, "backup", _("Backup"))

        self.add(self.stack)

    @staticmethod
    def __on_dark_theme_changed(_, state):
        gtk_settings = Gtk.Settings.get_default()
        gtk_settings.set_property("gtk-application-prefer-dark-theme",
                                  state)

    def __on_gpg_location_clicked(self, gpg_location_widget, _):
        from .utils import open_directory
        directory = open_directory(self)
        if directory:
            Settings.get_default().gpg_location = directory
            gpg_location_widget.secondary_lbl.set_text(directory)


    def __on_clear_database_clicked(self, *__):
        notification = Gd.Notification()
        notification.set_timeout(5)
        notification.connect("dismissed", self.__clear_database)
        container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        notification_lbl = Gtk.Label()
        notification_lbl.set_text(_("The existing accounts will be erased in 5 seconds"))
        container.pack_start(notification_lbl, False, False, 3)

        undo_btn = Gtk.Button()
        undo_btn.set_label(_("Undo"))
        undo_btn.connect("clicked", lambda widget: notification.hide())
        container.pack_end(undo_btn, False, False, 3)

        notification.add(container)
        notification_parent = self.stack.get_child_by_name("behaviour")
        notification_parent.add(notification)
        notification_parent.reorder_child(notification, 0)
        self.show_all()

    @staticmethod
    def __clear_database(*_):
        from ..models import Database, Keyring, AccountsManager
        from ..widgets.accounts import AccountsWidget
        Database.get_default().clear()
        Keyring.get_default().clear()
        AccountsManager.get_default().clear()
        AccountsWidget.get_default().clear()


