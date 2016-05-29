from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gio, Gdk, GObject
import logging
from TwoFactorAuth.models.settings import SettingsReader
from TwoFactorAuth.widgets.change_password import PasswordWindow
from gettext import gettext as _
from hashlib import md5


class SettingsWindow(Gtk.Window):

    def __init__(self, parent):
        self.parent = parent
        self.cfg = SettingsReader()
        self.generate_window()
        self.generate_compenents()
        self.show_all()

    def generate_window(self):
        Gtk.Window.__init__(self, title=_("Settings"), modal=True,
                            destroy_with_parent=True)
        self.connect("delete-event", lambda x, y: self.destroy())
        self.resize(300, 300)
        self.set_size_request(300, 300)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_transient_for(self.parent)

    def generate_compenents(self):
        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

        user_settings = self.generate_user_settings()
        user_settings.set_border_width(10)
        self.notebook.append_page(user_settings, Gtk.Label(_('Preferences')))

        login_settings = self.generate_login_settings()
        login_settings.set_border_width(10)
        self.notebook.append_page(login_settings, Gtk.Label(_('Account')))

    def generate_login_settings(self):
        mainbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        enable_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        enable_label = Gtk.Label(_("Enable password: "))
        enable_switch = Gtk.Switch()
        enable_switch.set_active(bool(self.cfg.read("state", "login")))
        enable_switch.connect("notify::active", self.on_switch_activated)

        enable_box.pack_start(enable_label, False, True, 0)
        enable_box.pack_end(enable_switch, False, True, 0)

        password_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        password_label = Gtk.Label(_("Password: "))
        password_button = Gtk.Button()
        password_button.get_style_context().add_class("flat")
        password_button.get_style_context().add_class("text-button")
        password_button.set_label("******")
        password_button.connect("clicked", self.new_password_window)

        password_box.pack_start(password_label, False, True, 0)
        password_box.pack_end(password_button, False, True, 0)

        mainbox.pack_start(enable_box, False, True, 6)
        mainbox.pack_start(password_box, False, True, 6)
        return mainbox

    def generate_user_settings(self):
        mainbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        time_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        time_label = Gtk.Label(_("Password generation time (s): "))
        default_value = self.cfg.read("refresh-time", "preferences")
        if default_value < 30 or default_value > 120:
            default_value = 30
        adjustment = Gtk.Adjustment(default_value, 10, 120, 1, 10, 0)
        time_spinbutton = Gtk.SpinButton()
        time_spinbutton.connect("value-changed", self.on_time_changed)
        time_spinbutton.set_adjustment(adjustment)
        time_spinbutton.set_value(default_value)

        time_box.pack_start(time_label, False, True, 0)
        time_box.pack_end(time_spinbutton, False, True, 0)

        mainbox.pack_start(time_box, False, True, 6)
        return mainbox

    def new_password_window(self, *args):
        PasswordWindow(self)

    def on_time_changed(self, spinbutton):
        self.cfg.update("refresh-time", spinbutton.get_value_as_int(),
                        "preferences")

    """ def on_password_changed(self, entry):
        password = md5(entry.get_text().encode('utf-8')).hexdigest()
        self.cfg.update("password", password, "login")
    """

    def on_switch_activated(self, switch, gparam):
        password_box = switch.get_parent().get_parent().get_children()[1]
        password_entry = password_box.get_children()[1]
        password_entry.set_sensitive(switch.get_active())
        self.cfg.update("state", switch.get_active(), "login")
