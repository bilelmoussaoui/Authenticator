from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk
from TwoFactorAuth.models.settings import SettingsReader
from TwoFactorAuth.widgets.change_password import PasswordWindow
from gettext import gettext as _


class SettingsWindow(Gtk.Window):
    notebook = Gtk.Notebook()
    time_spin_button = Gtk.SpinButton()
    enable_switch = Gtk.Switch()
    password_button = Gtk.Button()

    def __init__(self, parent):
        self.parent = parent
        self.cfg = SettingsReader()
        self.generate_window()
        self.generate_components()
        self.show_all()

    def generate_window(self):
        Gtk.Window.__init__(self, title=_("Settings"), modal=True,
                            destroy_with_parent=True)
        self.connect("delete-event", self.close_window)
        self.resize(300, 300)
        self.set_size_request(300, 300)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_transient_for(self.parent)

    def generate_components(self):
        """
            Generate all the components
        """
        self.add(self.notebook)
        user_settings = self.generate_user_settings()
        user_settings.set_border_width(10)
        self.notebook.append_page(user_settings, Gtk.Label(_('Preferences')))

        login_settings = self.generate_login_settings()
        login_settings.set_border_width(10)
        self.notebook.append_page(login_settings, Gtk.Label(_('Account')))

    def generate_login_settings(self):
        """
            Create a box with login settings components
            :return (Gtk.Box): Box contains all the components
        """
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        enable_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        enable_label = Gtk.Label(_("Enable password: "))
        self.enable_switch.set_active(bool(self.cfg.read("state", "login")))
        self.enable_switch.connect("notify::active", self.on_switch_activated)

        enable_box.pack_start(enable_label, False, True, 0)
        enable_box.pack_end(self.enable_switch, False, True, 0)

        password_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        password_label = Gtk.Label(_("Password: "))
        self.password_button.get_style_context().add_class("flat")
        self.password_button.get_style_context().add_class("text-button")
        self.password_button.set_label("******")
        self.password_button.connect("clicked", self.new_password_window)

        password_box.pack_start(password_label, False, True, 0)
        password_box.pack_end(self.password_button, False, True, 0)

        main_box.pack_start(enable_box, False, True, 6)
        main_box.pack_start(password_box, False, True, 6)
        return main_box

    def generate_user_settings(self):
        """
            Create a box with user settings components
            :return (Gtk.Box): Box contains all the components
        """
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        time_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        time_label = Gtk.Label(_("Password generation time (s): "))
        default_value = self.cfg.read("refresh-time", "preferences")
        if default_value < 30 or default_value > 120:
            default_value = 30
        adjustment = Gtk.Adjustment(default_value, 10, 120, 1, 10, 0)
        self.time_spin_button.connect("value-changed", self.on_time_changed)
        self.time_spin_button.set_adjustment(adjustment)
        self.time_spin_button.set_value(default_value)

        time_box.pack_start(time_label, False, True, 0)
        time_box.pack_end(self.time_spin_button, False, True, 0)

        main_box.pack_start(time_box, False, True, 6)
        return main_box

    def new_password_window(self, *args):
        """
            Show a new password window
        """
        PasswordWindow(self)

    def on_time_changed(self, spin_button):
        """
            Update time tog generate a new secret code
        """
        self.cfg.update("refresh-time", spin_button.get_value_as_int(),
                        "preferences")

    def on_switch_activated(self, switch, *args):
        """
            Update password state : enabled/disabled
        """
        self.password_button.set_sensitive(switch.get_active())
        self.cfg.update("state", switch.get_active(), "login")
        self.parent.app.refresh_menu()
        self.parent.refresh_menu_popover()

    def close_window(self, *args):
        """
            Close the window
        """
        self.destroy()