from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gio, Gdk
import logging


class ConfirmationMessage(Gtk.Window):
    def __init__(self, parent, message):
        try:
            self.dialog = Gtk.MessageDialog(
                                parent=parent,
                                flags=Gtk.DialogFlags.MODAL,
                                message_format=message,
                                buttons=Gtk.ButtonsType.OK_CANCEL)
            logging.debug("Confirmation message created successfully")
        except Exception as e:
            logging.error(str(e))

    def show(self):
        try:
            self.result = self.dialog.run()
            self.dialog.hide()
        except AttributeError:
            logging.error("Confiramation message was not created correctly")
            return None

    def get_confirmation(self):
        return self.result ==  Gtk.ResponseType.OK

    def destroy(self):
        self.dialog.destroy()
