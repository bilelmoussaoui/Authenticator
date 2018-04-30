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

from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk


class ActionsBar(Gtk.ActionBar):

    instance = None

    def __init__(self):
        Gtk.ActionBar.__init__(self)
        self._build_widgets()
        self.show_all()
        self.set_visible(False)
        self.set_no_show_all(True)

    @staticmethod
    def get_default():
        if ActionsBar.instance is None:
            ActionsBar.instance = ActionsBar()
        return ActionsBar.instance

    def _build_widgets(self):
        self.delete_btn = Gtk.Button(label=_("Delete"))
        self.delete_btn.set_sensitive(False)
        self.pack_end(self.delete_btn)

    def on_selected_rows_changed(self, accounts_list, selected_rows):
        self.delete_btn.set_sensitive(selected_rows > 0)
