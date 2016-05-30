from gi.repository import Gtk, Gio
import logging


class SettingsReader:
    path = "org.gnome.TwoFactorAuth"

    def __init__(self):
        try:
            # Check if the gsettings path exists
            self.source = Gio.SettingsSchemaSource.get_default()
            self.source.lookup(self.path, True)
        except Exception as e:
            logging.critical("Couldn't load gsettings source %s " % str(e))

    def read(self, key, path):
        """
            Read a 'key' from org.gnome.TwoFactorAuth.'path'
            :param key: (str) key to read
            :param path: login/user
            :return: value
        """
        gsettings = Gio.Settings.new(self.path + "." + path)
        value = gsettings.get_value(key)
        value_type = value.get_type_string()
        value = str(value).strip("'")
        if value_type == "i":
            return int(value)
        elif value_type == "b":
            return value == "true"
        else:
            return value

    def update(self, key, value, path):
        """
            Update 'key' value to 'value' from org.gnome.TwoFactorAuth.'path'
            :param key: (str) key to read
            :param value: updated value
            :param path: login/user
            :return: value
        """
        gsettings = Gio.Settings.new(self.path + "." + path)
        if type(value) is int:
            gsettings.set_int(key, value)
        elif type(value) is bool:
            gsettings.set_boolean(key, value)
        else:
            gsettings.set_string(key, value)
        gsettings.apply()
