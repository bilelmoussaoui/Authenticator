# -*- coding: utf-8 -*-
"""
 Copyright © 2016 Bilal Elmoussaoui <bil.elmoussaoui@gmail.com>

 This file is part of Gnome-TwoFactorAuth.

 Gnome-TwoFactorAuth is free software: you can redistribute it and/or
 modify it under the terms of the GNU General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.


 TwoFactorAuth is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Gnome-TwoFactorAuth. If not, see <http://www.gnu.org/licenses/>.
"""
from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, Gdk, GObject, GLib
from Authenticator.widgets.confirmation import ConfirmationMessage
from Authenticator.widgets.account_row import AccountRowGrid
from gettext import gettext as _
from hashlib import sha256
import logging


class AccountsGrid(Gtk.FlowBox):
    scrolled_win = None

    def __init__(self, window, accounts):
        self.accounts = accounts
        self.window = window
        self.generate()
        self.connect("child-activated", self.activate_child)
        self.connect("selected-children-changed", self.selected_child)
        GLib.timeout_add_seconds(1, self.refresh)

    def generate(self):
        Gtk.FlowBox.__init__(self,orientation=Gtk.Orientation.HORIZONTAL)
        # Create a ScrolledWindow for accounts
        self.set_min_children_per_line(2)
        self.set_max_children_per_line(8)
        self.set_valign(Gtk.Align.START)
        self.set_column_spacing(0)
        self.set_row_spacing(0)
        self.set_selection_mode(Gtk.SelectionMode.SINGLE)

        self.scrolled_win = Gtk.ScrolledWindow()
        self.scrolled_win.add_with_viewport(self)
        self.set_homogeneous(True)
        count = len(self.accounts)

        for account in self.accounts:
            self.add(AccountRowGrid(self, self.window, account))

        if count != 0:
            self.select_child(self.get_child_at_index(0))

        self.show_all()

    def selected_child(self, account_list):
        for box in self.get_children():
            row = box.get_children()[0]
            checkbutton = row.get_checkbox()
            if not checkbutton.get_active() and self.window.is_select_mode:
                self.unselect_child(box)

    def activate_child(self, account_list, selected_child):
        if self.window.is_select_mode and selected_child:
            selected_box = selected_child.get_children()[0]
            self.select_account(selected_box.get_checkbox())


    def toggle_select_mode(self):
        is_select_mode = self.window.is_select_mode
        if is_select_mode:
            self.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        else:
            self.set_selection_mode(Gtk.SelectionMode.SINGLE)
            if len(self.get_children()) != 0:
                self.select_child(self.get_child_at_index(0))

        for box in self.get_children():
            row = box.get_children()[0]
            checkbox = row.get_checkbox()
            code_label = row.get_code_label()
            visible = checkbox.get_visible()
            style_context = code_label.get_style_context()
            if is_select_mode:
                self.select_account(checkbox)
            row.toggle_action_box(visible)
            checkbox.set_visible(not visible)
            checkbox.set_no_show_all(visible)

    def remove_selected(self, *args):
        """
            Remove selected accounts
        """
        for row in self.get_selected_children():
            checkbox = row.get_checkbox()
            if checkbox.get_active():
                row.remove()
        self.unselect_all()
        self.window.toggle_select()
        self.window.refresh_window()

    def select_account(self, checkbutton):
        """
            Select an account
            :param checkbutton:
        """
        is_active = checkbutton.get_active()
        is_visible = checkbutton.get_visible()
        flowbox_child = checkbutton.get_parent().get_parent().get_parent().get_parent().get_parent()
        if is_active:
            self.select_child(flowbox_child)
        else:
            self.unselect_child(flowbox_child)
        selected_count = len(self.get_selected_children())
        self.window.hb.remove_button.set_sensitive(selected_count > 0)

    def get_selected_child_id(self):
        selected_box = self.get_selected_children()
        if selected_box:
            return selected_box[0].get_children()[0].account.get_id()
        else:
            return None

    def get_selected_row_id(self):
        return self.get_selected_child_id()

    def toggle(self, visible):
        self.set_visible(visible)
        self.set_no_show_all(not visible)
        self.get_scrolled_win().set_visible(visible)
        self.get_scrolled_win().set_no_show_all(not visible)

    def is_visible(self):
        return self.get_visible()

    def hide(self):
        self.toggle(False)

    def show(self):
        self.toggle(True)

    def get_scrolled_win(self):
        return self.scrolled_win

    def refresh(self):
        self.scrolled_win.hide()
        self.scrolled_win.show_all()

    def append(self, account):
        self.add(AccountRowGrid(self, self.window, account))
        self.refresh()

    def remove_by_id(self, _id):
        for row in self.get_children():
            row = row.get_children()[0]
            if row.account.get_id() == _id:
                self.remove(row)
                break
        self.refresh()
