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

require_version("Gd", "1.0")
require_version("Gtk", "3.0")
from gi.repository import Gd, Gtk, GObject, GLib
from os import path
from tempfile import NamedTemporaryFile

from ...models import GPG, Logger
from ..settings import SettingsBoxWithEntry, ClickableSettingsBox


class GPGRestoreWindow(Gtk.Window):
    def __init__(self, filename):
        Gtk.Window.__init__(self)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_size_request(400, 200)
        self.set_title(_("GPG paraphrase"))
        self.resize(400, 200)
        self._filename = filename
        self._build_widgets()

    def _build_widgets(self):
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_close_button(True)
        header_bar.set_title(_("GPG paraphrase"))
        apply_btn = Gtk.Button()
        apply_btn.set_label(_("Import"))
        apply_btn.get_style_context().add_class("suggested-action")
        apply_btn.connect("clicked", self.__on_apply)
        header_bar.pack_end(apply_btn)
        self.set_titlebar(header_bar)

        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.paraphrase_widget = SettingsBoxWithEntry(_("Paraphrase"), True)
        container.pack_start(self.paraphrase_widget, False, False, 0)
        container.get_style_context().add_class("settings-main-container")
        self.add(container)

    def __on_apply(self, *__):
        from ...models import BackupJSON
        try:
            paraphrase = self.paraphrase_widget.entry.get_text()
            if not paraphrase:
                paraphrase = " "
            output_file = path.join(GLib.get_user_cache_dir(),
                                    path.basename(NamedTemporaryFile().name))
            status = GPG.get_default().decrypt_json(self._filename, paraphrase, output_file)
            if status.ok:
                BackupJSON.import_file(output_file)
                self.destroy()
            else:
                self.__send_notification(_("There was an error during the import of the encrypted file."))

        except AttributeError:
            Logger.error("[GPG] Invalid JSON file.")

    def __send_notification(self, message):
        notification = Gd.Notification()
        notification.set_timeout(5)
        container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        notification_lbl = Gtk.Label()
        notification_lbl.set_text(message)
        container.pack_start(notification_lbl, False, False, 3)

        notification.add(container)
        notification_parent = self.get_children()[-1]
        notification_parent.add(notification)
        notification_parent.reorder_child(notification, 0)
        self.show_all()


class FingprintPGPWindow(Gtk.Window, GObject.GObject):
    """Main Window object."""
    __gsignals__ = {
        'selected': (GObject.SignalFlags.RUN_LAST, None, (str,))
    }

    def __init__(self, filename):
        Gtk.Window.__init__(self)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_size_request(600, 600)
        self.set_title(_("GPG fingerprint"))
        self.resize(600, 600)
        self._filename = filename
        self._build_widgets()

    def _build_widgets(self):
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_close_button(True)
        header_bar.set_title(_("GPG fingerprint"))
        self.set_titlebar(header_bar)

        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        keys = GPG.get_default().get_keys()
        self.__add_keys(keys["public"], _("Public keys"), container)
        self.__add_keys(keys["private"], _("Private keys"), container)

        container.get_style_context().add_class("settings-main-container")
        self.add(container)

    def __add_keys(self, keys, label, container):
        key_label = Gtk.Label()
        key_label.set_halign(Gtk.Align.START)
        key_label.get_style_context().add_class("gpg-key-lbl")
        key_label.set_text(label)
        container.pack_start(key_label, False, False, 0)

        for key in keys:
            uid = key.get("uids", [""])[0]
            fingerprint = key.get("fingerprint", "")
            key_widget = ClickableSettingsBox(uid, fingerprint)
            key_widget.connect("button-press-event", self.__finger_print_selected, fingerprint)
            container.pack_start(key_widget, False, False, 0)

    def __finger_print_selected(self, _, __, fingerprint):
        self.emit("selected", fingerprint)
        self.destroy()
