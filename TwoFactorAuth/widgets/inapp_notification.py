from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, GLib
from gettext import gettext as _
import logging


class InAppNotification(Gtk.Revealer):
    timer = 0

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
        frame = Gtk.Frame()
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        frame.props.width_request = 100
        frame.get_style_context().add_class("app-notification")

        self.undo_button = Gtk.Button()
        self.undo_button.set_label(_("Undo"))
        if self.undo_action is not None:
            self.undo_button.connect("clicked", self.undo_action)
        else:
            self.undo_button.set_visible(False)
            self.undo_button.set_no_show_all(True)

        delete_button = Gtk.Button()
        delete_icon = Gio.ThemedIcon(name="edit-delete-symbolic")
        delete_image = Gtk.Image.new_from_gicon(
            delete_icon, Gtk.IconSize.BUTTON)
        delete_button.set_tooltip_text(_("Hide notification"))
        delete_button.set_image(delete_image)
        delete_button.connect("clicked", self.on_hide_notification)

        self.message_label = Gtk.Label()
        self.message_label.set_text(self.message)

        self.main_box.pack_end(delete_button, False, False, 6)
        self.main_box.pack_end(self.undo_button, False, False, 6)
        self.main_box.pack_start(self.message_label, False, False, 6)
        frame.add(self.main_box)
        self.add(frame)

    def on_hide_notification(self, *args):
        self.hide()

    def show(self):
        self.set_reveal_child(True)

    def hide(self):
        self.set_reveal_child(False)

    def update(self, message, undo_action = None):
        self.message_label.set_text(message)
        self.timer = 0
        if undo_action is not None:
            self.undo_button.set_visible(True)
            self.undo_button.set_no_show_all(False)
            self.undo_action = undo_action
            self.undo_button.connect("clicked", self.undo_action)

    def update_timer(self):
        if self.get_reveal_child():
            if self.timer == self.timeout:
                self.hide()
                self.timer = 0
            else:
                self.timer += 1
        return True
