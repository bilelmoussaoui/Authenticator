"""
 Copyright © 2017 Bilal Elmoussaoui <bil.elmoussaoui@gmail.com>

 This file is part of Gnome Authenticator.

 Gnome Authenticator is free software: you can redistribute it and/or
 modify it under the terms of the GNU General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 TwoFactorAuth is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Gnome Authenticator. If not, see <http://www.gnu.org/licenses/>.
"""
from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk


class AboutDialog(Gtk.AboutDialog):
    """AboutDialog Widget."""

    def __init__(self):
        Gtk.AboutDialog.__init__(self)
        self.set_modal(True)
        self._build_widgets()

    def _build_widgets(self):
        """Build the AboutDialog widget."""
        self.set_authors(["Bilal Elmoussaoui"])
        self.set_artists(["Alexandros Felekidis"])
        self.set_logo_icon_name("org.gnome.Authenticator")
        self.set_license_type(Gtk.License.GPL_3_0)
        self.set_program_name(_("Gnome Authenticator"))
        self.set_translator_credits(_("translator-credits"))
        self.set_version("0.2")
        self.set_comments(_("Two factor authentication codes generator."))
        self.set_website("https://github.com/bil-elmoussaoui/Gnome-Authenticator")
