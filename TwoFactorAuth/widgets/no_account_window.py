from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk
import logging
from gettext import gettext as _

class NoAccountWindow(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL,
                            spacing=6)
        self.generate_box()

    def generate_box(self):
        logo_image = Gtk.Image()
        logo_image.set_from_icon_name("dialog-information-symbolic",
                                      Gtk.IconSize.DIALOG)
        no_apps_label = Gtk.Label()
        no_apps_label.set_text(_("There's no account at the moment"))

        self.pack_start(logo_image, False, False, 6)
        self.pack_start(no_apps_label, False, False, 6)

    def toggle(self, visible):
        self.set_visible(visible)
        self.set_no_show_all(not visible)

    def hide(self):
        self.toggle(False)

    def show(self):
        self.toggle(True)
