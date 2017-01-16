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
import logging
from Authenticator.const import settings
from Authenticator.widgets.account_row import AccountRowGrid, AccountRowList
from Authenticator.widgets.confirmation import ConfirmationMessage
from gettext import gettext as _
from gi.repository import GLib, GObject, Gdk, Gio, Gtk
from hashlib import sha256


class AccountsGrid(Gtk.FlowBox):

    def __init__(self, window, accounts):
        self.accounts = accounts
        self.window = window
        self.generate()
        self.accel = Gtk.AccelGroup()
        self.window.add_accel_group(self.accel)
        self.connect("child-activated", self.activate_child)
        self.connect("selected-children-changed", self.selected_child)
        self.accel.connect(Gdk.keyval_from_name('Up'), Gdk.ModifierType.META_MASK, 0, self.navigate)
        self.accel.connect(Gdk.keyval_from_name('Down'), Gdk.ModifierType.META_MASK, 0, self.navigate)
        self.accel.connect(Gdk.keyval_from_name('Left'), Gdk.ModifierType.META_MASK, 0, self.navigate)
        self.accel.connect(Gdk.keyval_from_name('Right'), Gdk.ModifierType.META_MASK, 0, self.navigate)

    def navigate(self, *args):
        """
            Keyboard Listener handling
        """
        keyname = Gdk.keyval_name(args[2]).lower()
        if not settings.get_is_locked():
            count = len(self.get_children())
            selected_row = self.get_selected_children()
            if selected_row is not None:
                index = selected_row[0].get_index()
                child_per_line = self.get_children_per_line()
                if keyname in ["up", "down"]:
                    dy = -child_per_line if keyname == "up" else child_per_line
                    new_index = (index + dy) % count
                else:
                    dx = -1 if keyname == "left" else 1
                    new_index = (index + dx) % count
                self.select_child(self.get_child_at_index(new_index))
                return True
        return False

    def generate(self):
        Gtk.FlowBox.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)

        self.set_min_children_per_line(2)
        self.set_max_children_per_line(8)
        self.set_valign(Gtk.Align.START)
        self.set_column_spacing(0)
        self.set_row_spacing(0)
        self.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.set_homogeneous(True)
        count = len(self.accounts)

        for account in self.accounts:
            self.add(AccountRowGrid(self, self.window, account))

        if count != 0:
            self.select_child(self.get_child_at_index(0))

    def selected_child(self, account_list):
        for row in self.get_children():
            checkbutton = row.get_checkbox()
            if not checkbutton.get_active() and self.window.is_select_mode:
                self.unselect_child(row)

    def get_children_per_line(self):
        total = len(self.get_children())
        child_allocated_width = self.get_children()[0].get_allocated_width()
        window_allocated_width = self.window.get_allocated_width()
        return round(window_allocated_width/child_allocated_width,0)

    def activate_child(self, account_list, selected_child):
        if self.window.is_select_mode and selected_child:
            self.select_account(selected_child.get_checkbox())

    def toggle_select_mode(self):
        is_select_mode = self.window.is_select_mode
        if is_select_mode:
            self.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        else:
            self.set_selection_mode(Gtk.SelectionMode.SINGLE)
            if len(self.get_children()) != 0:
                self.select_child(self.get_child_at_index(0))

        for row in self.get_children():
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
        print(self.get_selected_children())
        for row in self.get_selected_children():
            checkbox = row.get_checkbox()
            if checkbox.get_active():
                row.remove()
        self.unselect_all()
        self.window.toggle_select()

    def select_account(self, checkbutton):
        """
            Select an account
            :param checkbutton:
        """
        is_active = checkbutton.get_active()
        is_visible = checkbutton.get_visible()
        flowbox_child = checkbutton.get_parent().get_parent().get_parent().get_parent()
        if is_active:
            self.select_child(flowbox_child)
        else:
            self.unselect_child(flowbox_child)
        selected_count = len(self.get_selected_children())
        self.window.hb.remove_button.set_sensitive(selected_count > 0)

    def get_selected_child_id(self):
        selected_box = self.get_selected_children()
        if selected_box:
            return selected_box[0].account.get_id()
        else:
            return None

    def get_selected_row_id(self):
        return self.get_selected_child_id()

    def append(self, account):
        self.add(AccountRowGrid(self, self.window, account))

    def remove_by_id(self, _id):
        for row in self.get_children():
            if row.account.get_id() == _id:
                self.remove(row)
                break


class AccountsList(Gtk.ListBox):

    def __init__(self, window, accounts):
        self.accounts = accounts
        self.window = window
        self.generate()
        self.accel = Gtk.AccelGroup()
        self.window.add_accel_group(self.accel)
        self.connect("row-activated", self.activate_row)
        self.connect("row-selected", self.selected_row)
        self.accel.connect(Gdk.keyval_from_name('Up'), Gdk.ModifierType.META_MASK, 0, self.navigate)
        self.accel.connect(Gdk.keyval_from_name('Down'), Gdk.ModifierType.META_MASK, 0, self.navigate)

    def generate(self):
        Gtk.ListBox.__init__(self)
        self.get_style_context().add_class("applications-list")
        self.set_adjustment()
        self.set_selection_mode(Gtk.SelectionMode.SINGLE)

        count = len(self.accounts)

        for account in self.accounts:
            self.add(AccountRowList(self, self.window, account))

        if count != 0:
            self.select_row(self.get_row_at_index(0))

    def selected_row(self, account_list, selected_row):
        for row in self.get_children():
            if row != selected_row:
                row.toggle_edit_mode(False)
            checkbutton = row.get_checkbox()
            if not checkbutton.get_active() and self.window.is_select_mode:
                self.unselect_row(row)

    def activate_row(self, account_list, selected_row):
        if self.window.is_select_mode and selected_row:
            self.select_account(selected_row.get_checkbox())

    def navigate(self, *args):
        """
            Keyboard Listener handling
        """
        keyname = Gdk.keyval_name(args[2]).lower()
        if not settings.get_is_locked():
            count = len(self.get_children())
            dx = -1 if keyname == "up" else 1
            selected_row = self.get_selected_row()
            if selected_row is not None:
                index = selected_row.get_index()
                new_index = (index + dx) % count
                self.select_row(self.get_row_at_index(new_index))
                return True
        return False


    def toggle_select_mode(self):
        is_select_mode = self.window.is_select_mode
        if is_select_mode:
            self.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        else:
            self.set_selection_mode(Gtk.SelectionMode.SINGLE)
            if len(self.get_children()) != 0:
                self.select_row(self.get_row_at_index(0))

        for row in self.get_children():
            checkbox = row.get_checkbox()
            code_label = row.get_code_label()
            visible = checkbox.get_visible()
            style_context = code_label.get_style_context()
            if is_select_mode:
                self.select_account(checkbox)
                style_context.add_class("application-secret-code-select-mode")
            else:
                style_context.remove_class(
                    "application-secret-code-select-mode")
            row.toggle_action_box(visible)
            checkbox.set_visible(not visible)
            checkbox.set_no_show_all(visible)

    def remove_selected(self, *args):
        """
            Remove selected accounts
        """
        for row in self.get_selected_rows():
            checkbox = row.get_checkbox()
            if checkbox.get_active():
                row.remove()
        self.unselect_all()
        self.window.toggle_select()

    def select_account(self, checkbutton):
        """
            Select an account
            :param checkbutton:
        """
        is_active = checkbutton.get_active()
        is_visible = checkbutton.get_visible()
        listbox_row = checkbutton.get_parent().get_parent().get_parent()
        if is_active:
            self.select_row(listbox_row)
        else:
            self.unselect_row(listbox_row)
        selected_count = len(self.get_selected_rows())
        self.window.hb.remove_button.set_sensitive(selected_count > 0)

    def get_selected_row_id(self):
        selected_row = self.get_selected_row()
        if selected_row:
            return selected_row.account.get_id()
        else:
            return None

    def append(self, account):
        self.add(AccountRowList(self, self.window, account))

    def remove_by_id(self, _id):
        for row in self.get_children():
            if row.account.get_id() == _id:
                self.remove(row)
                break
