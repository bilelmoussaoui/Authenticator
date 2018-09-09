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
from abc import abstractmethod, ABCMeta

from gi import require_version

require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio
from gettext import gettext as _

from ..models import Database


class HeaderBarState:
    EMPTY = 0
    NORMAL = 2
    SELECT = 3


class HeaderBarBtn:
    __metaclass__ = ABCMeta

    def __init__(self, icon_name, tooltip):
        self._build(icon_name, tooltip)

    @abstractmethod
    def set_image(self, image):
        """Set an image"""

    @abstractmethod
    def set_tooltip_text(self, tooltip):
        """Set the tooltip text"""

    def _build(self, icon_name, tooltip):
        """
        :param icon_name:
        :param tooltip:
        """
        icon = Gio.ThemedIcon(name=icon_name)
        image = Gtk.Image.new_from_gicon(icon,
                                         Gtk.IconSize.BUTTON)
        self.set_tooltip_text(tooltip)
        self.set_image(image)

    def hide_(self):
        """Set a button visible or not?."""
        self.set_visible(False)
        self.set_no_show_all(True)

    def show_(self):
        self.set_visible(True)
        self.set_no_show_all(False)


class HeaderBarButton(Gtk.Button, HeaderBarBtn):
    """HeaderBar Button widget"""

    def __init__(self, icon_name, tooltip):
        Gtk.Button.__init__(self)
        HeaderBarBtn.__init__(self, icon_name, tooltip)


class HeaderBarToggleButton(Gtk.ToggleButton, HeaderBarBtn):
    """HeaderBar Toggle Button widget"""

    def __init__(self, icon_name, tooltip):
        Gtk.ToggleButton.__init__(self)
        HeaderBarBtn.__init__(self, icon_name, tooltip)


class HeaderBar(Gtk.HeaderBar):
    """
    HeaderBar widget
    """
    instance = None
    state = HeaderBarState.NORMAL

    def __init__(self):
        Gtk.HeaderBar.__init__(self)

        self.search_btn = HeaderBarToggleButton("system-search-symbolic",
                                                _("Search"))
        self.add_btn = HeaderBarButton("list-add-symbolic",
                                       _("Add a new account"))
        self.settings_btn = HeaderBarButton("open-menu-symbolic",
                                            _("Settings"))
        self.select_btn = HeaderBarButton("object-select-symbolic",
                                          _("Selection mode"))

        self.cancel_btn = Gtk.Button(label=_("Cancel"))

        self.popover = None

        self._build_widgets()

    @staticmethod
    def get_default():
        """
        :return: Default instance of HeaderBar
        """
        if HeaderBar.instance is None:
            HeaderBar.instance = HeaderBar()
        return HeaderBar.instance

    def _build_widgets(self):
        """
        Generate the HeaderBar widgets
        """
        self.set_show_close_button(True)

        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        # Hide the search button if nothing is found
        if Database.get_default().count > 0:
            self.search_btn.show_()
        else:
            self.search_btn.hide_()

        left_box.add(self.add_btn)

        right_box.pack_start(self.search_btn, False, False, 0)
        right_box.pack_start(self.select_btn, False, False, 0)
        right_box.pack_start(self.cancel_btn, False, False, 0)
        right_box.pack_end(self.settings_btn, False, False, 3)

        self.pack_start(left_box)
        self.pack_end(right_box)

    def generate_popover_menu(self, menu):
        self.settings_btn.connect("clicked", self.toggle_popover)
        self.popover = Gtk.Popover.new_from_model(self.settings_btn,
                                                  menu)
        self.popover.props.width_request = 200

    def toggle_popover(self, *_):
        if self.popover:
            if self.popover.get_visible():
                self.popover.hide()
            else:
                self.popover.show_all()

    def toggle_settings_button(self, visible):
        self.settings_button.set_visible(visible)
        self.settings_button.set_no_show_all(not visible)

    def set_state(self, state):
        if state != HeaderBarState.SELECT:
            self.cancel_btn.set_visible(False)
            self.cancel_btn.set_no_show_all(True)
        if state == HeaderBarState.EMPTY:
            self.add_btn.show_()
            self.search_btn.hide_()
            self.select_btn.hide_()
            self.settings_btn.show_()
        elif state == HeaderBarState.SELECT:
            self.search_btn.show_()
            self.add_btn.hide_()
            self.select_btn.hide_()
            self.set_show_close_button(False)
            self.get_style_context().add_class("selection-mode")
            self.cancel_btn.set_visible(True)
            self.cancel_btn.set_no_show_all(False)
            self.settings_btn.hide_()
            self.set_title(_("Click on items to select them"))
        else:
            self.search_btn.show_()
            self.add_btn.show_()
            self.select_btn.show_()
            self.settings_btn.show_()
        if self.state == HeaderBarState.SELECT:
            self.get_style_context().remove_class("selection-mode")
            self.set_show_close_button(True)
            self.set_title("")
        self.state = state
