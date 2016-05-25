from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gio, Gdk
from ui.window import TwoFactorWindow
import logging
from models.provider import Provider

logging.basicConfig(level=logging.DEBUG,
                format='[%(levelname)s] %(message)s',
                )

# TODO : https://pypi.python.org/pypi/pyotp


class TwoFactor(Gtk.Application):
    win = None

    def __init__(self):
        Gtk.Application.__init__(self,
                                 application_id='org.gnome.twofactor',
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)
        GLib.set_application_name("Two-factor")
        GLib.set_prgname('twofactor')

        provider = Gtk.CssProvider()
        css_file = "/home/bilal/Projects/Two-factor-gtk/data/style.css"
        try:
            provider.load_from_path(css_file) #load css file
            Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),
                                            provider,
                                            Gtk.STYLE_PROVIDER_PRIORITY_USER)
            logging.debug("[CSS]: Loading css file %s" % css_file)
        except Exception as e:
            logging.debug("[CSS]: File not found %s" % css_file)
            logging.debug("[CSS]: Error message %s" % str(e))

    def do_startup(self):
        Gtk.Application.do_startup(self)

        action = Gio.SimpleAction.new("shortcuts", None)
        action.connect("activate", self.on_shortcuts)
        self.add_action(action)

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)

        builder = Gtk.Builder()
        builder.add_from_file("/home/bilal/Projects/Two-factor-gtk/data/menu.glade")
        logging.debug("[APP MENU] : adding gnome shell menu")
        self.set_app_menu(builder.get_object("app-menu"))

    def do_activate(self, *args):
        self.provider = Provider()
        if not self.win:
            TwoFactorWindow(self)
        self.win.show()
        self.add_window(self.win)

    def on_shortcuts(self, *args):
        logging.debug("Shortcuts window")
        self.win.show_shortcuts()

    def on_about(self, *args):
        logging.debug("About window")
        self.win.show_about()

    def on_quit(self, *args):
        Gtk.main_quit()
        self.win.destroy()
        self.quit()



app = TwoFactor()
app.run(None)
