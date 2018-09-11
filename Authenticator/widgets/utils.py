from gettext import gettext as _

from gi import require_version

require_version("Gtk", "3.0")
from gi.repository import Gtk


def __open_file_chooser(parent, mimetype, action=Gtk.FileChooserAction.OPEN):
    file_chooser = Gtk.FileChooserNative()
    file_chooser.set_action(action)
    file_chooser.set_transient_for(parent)
    filter_json = Gtk.FileFilter()
    filter_json.set_name(mimetype["name"])
    filter_json.add_mime_type(mimetype["type"])
    file_chooser.add_filter(filter_json)
    response = file_chooser.run()
    if response == Gtk.ResponseType.ACCEPT:
        filename = file_chooser.get_filename()
        return filename
    file_chooser.destroy()
    return None


def import_json(parent):
    mimetype = {'type': "application/json", 'name': _("JSON files")}
    return __open_file_chooser(parent, mimetype)


def export_json(parent):
    mimetype = {'type': "application/json", 'name': _("JSON files")}
    return __open_file_chooser(parent, mimetype, Gtk.FileChooserAction.SAVE)


def import_pgp_json(parent):
    mimetype = {'type': "application/pgp-encrypted", 'name': _("Encrypted GPG files")}
    return __open_file_chooser(parent, mimetype)


def export_pgp_json(parent):
    mimetype = {'type': "application/pgp-encrypted", 'name': _("Encrypted GPG files")}
    return __open_file_chooser(parent, mimetype, Gtk.FileChooserAction.SAVE)


def open_directory(parent):
    file_chooser = Gtk.FileChooserNative()
    file_chooser.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
    file_chooser.set_transient_for(parent)
    file_chooser.set_show_hidden(True)
    response = file_chooser.run()
    if response == Gtk.ResponseType.ACCEPT:
        filename = file_chooser.get_filename()
        return filename
    file_chooser.destroy()
    return None
