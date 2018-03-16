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
import logging
from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, GLib


class InAppNotification(Gtk.Revealer):
    timer = 0
    killed = False

    def __init__(self, message="", undo_action=None, timeout=5):
        Gtk.Revealer.__init__(self)
        self.timeout = timeout
        self.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self.message = message
        self.undo_action = undo_action
        self.generate_components()
        GLib.timeout_add_seconds(1, self.update_timer)

    def generate_components(self):
        self.get_style_context().add_class("top")
        self.infobar = Gtk.InfoBar()
        self.infobar.set_show_close_button(True)
        self.infobar.connect("response", self.response)
        self.infobar.set_default_response(Gtk.ResponseType.CLOSE)
        self.infobar.set_message_type(Gtk.MessageType.INFO)

        content_area = self.infobar.get_content_area()
        action_area = self.infobar.get_action_area()
        self.undo_button = None
        if self.undo_action:
            self.undo_button = self.infobar.add_button(_("Undo"), 
                                                        Gtk.ResponseType.CANCEL)

        self.message_label = Gtk.Label()
        self.message_label.set_text(self.message)

        content_area.add(self.message_label)
        self.add(self.infobar)

    def set_message_type(self, message_type):
        self.infobar.set_message_type(message_type)

    def on_hide_notification(self, *args):
        self.hide()

    def show(self):
        self.set_reveal_child(True)

    def hide(self):
        self.set_reveal_child(False)

    def set_message(self, message):
        self.message_label.set_text(message)
        self.timer = 0

    def set_undo_action(self, undo_action):
        if undo_action:
            if not self.undo_button:
                self.undo_button = self.infobar.add_button(_("Undo"), 
                                                            Gtk.ResponseType.CANCEL)
            else:
                self.undo_button.set_visible(True)
                self.undo_button.set_no_show_all(False)
            self.undo_action = undo_action
        else:
            if self.undo_button:
                self.undo_button.set_visible(False)
                self.undo_button.set_no_show_all(True)

    def response(self, infobar, response_id):
        if response_id == Gtk.ResponseType.CLOSE:
            self.hide()
        elif response_id == Gtk.ResponseType.CANCEL:
            self.undo_action()

    def update_timer(self):
        if self.get_reveal_child() and not self.killed:
            if self.timer == self.timeout:
                self.hide()
                self.timer = 0
            else:
                self.timer += 1
            return True
        return False
