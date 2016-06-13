from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, Gdk, GObject, GLib
from TwoFactorAuth.widgets.add_account import AddAccount
from TwoFactorAuth.widgets.confirmation import ConfirmationMessage
from TwoFactorAuth.widgets.account_row import AccountRow
from TwoFactorAuth.widgets.search_bar import SearchBar
from TwoFactorAuth.widgets.login_window import LoginWindow
from TwoFactorAuth.widgets.no_account_window import NoAccountWindow
from TwoFactorAuth.widgets.headerbar import HeaderBar
import logging
from hashlib import sha256
from gettext import gettext as _


class Window(Gtk.ApplicationWindow):
    app = None
    selected_app_idx = None
    selected_count = 0
    counter = 0

    hb = None
    main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    login_box = None
    no_account_box = None
    apps_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    apps_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

    list_box = Gtk.ListBox()


    def __init__(self, application):
        self.app = application
        self.generate_window()
        self.generate_header_bar()
        self.generate_search_bar()
        self.generate_accounts_list()
        self.generate_no_accounts_box()
        self.generate_login_form()
        self.refresh_window()
        GLib.timeout_add_seconds(60, self.refresh_counter)

    def generate_window(self, *args):
        """
            Generate application window (Gtk.Window)
        """
        Gtk.ApplicationWindow.__init__(self, type=Gtk.WindowType.TOPLEVEL,
                                       application=self.app)
        self.move_latest_position()
        self.set_wmclass("Gnome-TwoFactorAuth", "Gnome TwoFactorAuth")
        self.set_icon_name("Gnome-TwoFactorAuth")
        self.resize(420, 550)
        self.set_size_request(420, 550)
        self.set_resizable(False)
        self.connect("key_press_event", self.on_key_press)
        self.connect("delete-event", lambda x, y: self.app.on_quit())
        self.add(self.main_box)

    def on_key_press(self, app, key_event):
        """
            Keyboard Listener handling
        """
        keypress = Gdk.keyval_name(key_event.keyval).lower()
        if not self.app.locked:
            control_mask = Gdk.ModifierType.CONTROL_MASK
            count = self.app.db.count()
            if keypress == "c":
                if key_event.state == control_mask:
                    self.copy_code()
            elif keypress == "l":
                if key_event.state == control_mask:
                    self.login_box.toggle_lock()
            elif keypress == "f":
                if key_event.state == control_mask:
                    self.hb.toggle_search()
            elif keypress == "s":
                if key_event.state == control_mask:
                    self.toggle_select()
            elif keypress == "n":
                if key_event.state == control_mask:
                    self.add_account()
            elif keypress == "delete" and not self.search_bar.is_visible():
                self.remove_account()
            elif keypress == "return":
                if count > 0:
                    if self.list_box.get_selected_row():
                        index = self.list_box.get_selected_row().get_index()
                    else:
                        index = 0
                    self.list_box.get_row_at_index(index).toggle_code_box()
            elif keypress == "backspace":
                if self.search_bar.is_empty():
                    self.hb.search_button.set_active(False)
            elif keypress == "escape":
                if self.search_bar.is_visible():
                    self.hb.search_button.set_active(False)
                if not self.select_button.get_visible():
                    self.toggle_select()
            elif keypress == "up" or keypress == "down":
                dx = -1 if keypress == "up" else 1
                if count != 0:
                    row = self.list_box.get_selected_row()
                    if row:
                        index = row.get_index()
                        index = (index + dx)%count
                        selected_row = self.list_box.get_row_at_index(index)
                        self.list_box.select_row(selected_row)
        else:
            if keypress == "return":
                self.login_box.on_unlock()

    def refresh_counter(self):
        """
            Add a value to the counter each 60 seconds
        """
        if not self.app.locked:
            self.counter += 1
        if self.app.cfg.read("auto-lock", "preferences"):
            if self.counter == self.app.cfg.read("auto-lock-time", "preferences") - 1:
                self.counter = 0
                self.toggle_lock()
        return True

    def generate_search_bar(self):
        """
            Generate search bar box and entry
        """
        self.search_bar = SearchBar(self.list_box)
        self.hb.search_button.connect("toggled", self.search_bar.toggle)

        self.apps_box.pack_start(self.search_bar, False, True, 0)
        self.main_box.pack_start(self.apps_box, True, True, 0)

    def remove_selected(self, *args):
        """
            Remove selected accounts
        """
        message = _("Do you really want to remove selected accounts?")
        confirmation = ConfirmationMessage(self, message)
        confirmation.show()
        if confirmation.get_confirmation():
            for row in self.list_box.get_children():
                checkbox = row.get_checkbox()
                if checkbox.get_active():
                    label_id = row.get_id()
                    row.kill()
                    self.app.db.remove_by_id(label_id)
                    self.list_box.remove(row)
            self.list_box.unselect_all()
        confirmation.destroy()
        self.toggle_select()
        self.refresh_window()

    def generate_login_form(self):
        """
            Generate login form
        """
        self.login_box = LoginWindow(self.app)
        self.hb.lock_button.connect("clicked", self.login_box.toggle_lock)
        self.main_box.pack_start(self.login_box, True, False, 0)

    def toggle_boxes(self, apps_box, no_apps_box, login_box):
        """
            Change the status of all the boxes in one time
            :param apps_box: bool
            :param no_apps_box: bool
            :param login_box: bool
            :return:
        """
        self.apps_box.set_visible(apps_box)
        self.apps_box.set_no_show_all(not apps_box)

    def generate_header_bar(self):
        """
            Generate a header bar box
        """
        self.hb = HeaderBar(self.app)
        # connect signals
        self.hb.cancel_button.connect("clicked", self.toggle_select)
        self.hb.select_button.connect("clicked", self.toggle_select)
        self.hb.remove_button.connect("clicked", self.remove_selected)
        self.hb.add_button.connect("clicked", self.add_account)
        self.set_titlebar(self.hb)

    def add_account(self, *args):
        """
            Create add application window
        """
        add_account = AddAccount(self)
        add_account.show_window()

    def toggle_select(self, *args):
        """
            Toggle select mode
        """
        self.hb.toggle_select_mode()
        pass_enabled = self.app.cfg.read("state", "login")
        is_visible = self.hb.is_on_select_mode()
        if not is_visible:
            self.list_box.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        else:
            self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)

            if self.selected_app_idx:
                index = self.selected_app_idx
            else:
                index = 0
            list_row_box = self.list_box.get_row_at_index(index)
            self.list_box.select_row(list_row_box)

        for row in self.list_box.get_children():
            checkbox = row.get_checkbox()
            code_label = row.get_code_label()
            visible = checkbox.get_visible()
            selected = checkbox.get_active()
            if not is_visible:
                self.select_account(checkbox)
                code_label.get_style_context().add_class("application-secret-code-select-mode")
            else:
                code_label.get_style_context().remove_class(
                    "application-secret-code-select-mode")

            checkbox.set_visible(not visible)
            checkbox.set_no_show_all(visible)

    def select_account(self, checkbutton):
        """
            Select an account
            :param checkbutton:
        """
        is_active = checkbutton.get_active()
        is_visible = checkbutton.get_visible()
        listbox_row = checkbutton.get_parent().get_parent().get_parent()
        if is_active:
            self.list_box.select_row(listbox_row)
            if is_visible:
                self.selected_count += 1
        else:
            self.list_box.unselect_row(listbox_row)
            if is_visible:
                self.selected_count -= 1
        self.hb.remove_button.set_sensitive(self.selected_count > 0)

    def select_row(self, list_box, listbox_row):
        """
            Select row @override the clicked event by default for ListBoxRow
        """
        index = listbox_row.get_index()
        is_select_mode = self.hb.is_on_select_mode()
        checkbox = listbox_row.get_checkbox()
        if is_select_mode:
            checkbox.set_active(not checkbox.get_active())
        else:
            if self.selected_app_idx:
                selected_row = self.list_box.get_row_at_index(
                    self.selected_app_idx)
                if selected_row:
                    self.list_box.unselect_row(selected_row)
            self.selected_app_idx = index
            self.list_box.select_row(self.list_box.get_row_at_index(index))

    def generate_accounts_list(self):
        """
            Generate an account ListBox inside of a ScrolledWindow
        """
        count = self.app.db.count()

        # Create a ScrolledWindow for accounts
        self.list_box.get_style_context().add_class("applications-list")
        self.list_box.set_adjustment()
        self.list_box.connect("row_activated", self.select_row)
        self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.apps_list_box.pack_start(self.list_box, True, True, 0)

        scrolled_win = Gtk.ScrolledWindow()
        scrolled_win.add_with_viewport(self.apps_list_box)
        self.apps_box.pack_start(scrolled_win, True, True, 0)

        apps = self.app.db.fetch_apps()
        i = 0
        count = len(apps)
        while i < count:
            self.list_box.add(AccountRow(self, apps[i][0], apps[i][1], apps[i][2],
                                         apps[i][3]))
            i += 1

    def generate_no_accounts_box(self):
        """
            Generate a box with no accounts message
        """
        self.no_account_box = NoAccountWindow()
        self.main_box.pack_start(self.no_account_box, True, False, 0)

    def append_list_box(self, uid, name, secret_code, image):
        """
            Add an element to the ListBox
            :param uid: account id
            :param name: account name
            :param secret_code: account secret code
            :param image: account image path or icon name
        """
        secret_code = sha256(secret_code.encode('utf-8')).hexdigest()
        self.list_box.add(AccountRow(self, uid, name, secret_code, image))
        self.list_box.show_all()

    def copy_code(self, *args):
        """
            Copy the secret code to clipboard
        """
        if len(args) > 0:
            # if the code is called by clicking on copy button, select the
            # right ListBowRow
            row = args[0].get_parent().get_parent().get_parent()
            self.list_box.select_row(row)
        selected_row = self.list_box.get_selected_row()
        code = selected_row.get_code()
        try:
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            clipboard.clear()
            clipboard.set_text(code, len(code))
            logging.debug("Secret code copied to clipboard")
        except Exception as e:
            logging.error(str(e))

    def refresh_window(self):
        """
            Refresh windows components
        """
        is_locked = self.app.locked
        count = self.app.db.count()
        if is_locked:
            self.login_box.show()
            self.no_account_box.hide()
            self.toggle_boxes(False, False, True)
        else:
            self.login_box.hide()
            if count == 0:
                self.no_account_box.show()
                self.toggle_boxes(False, True, False)
            else:
                self.no_account_box.hide()
                self.toggle_boxes(True, False, False)
        self.hb.refresh()
        self.main_box.show_all()
        self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)


    def remove_account(self, *args):
        """
            Remove an application
        """
        if len(args) > 0:
            row = args[0].get_parent().get_parent().get_parent()
            self.list_box.select_row(row)

        message = _("Do you really want to remove this account?")
        confirmation = ConfirmationMessage(self, message)
        confirmation.show()
        if confirmation.get_confirmation():
            if self.list_box.get_selected_row():
                selected_row = self.list_box.get_selected_row()
                app_id = selected_row.get_id()
                selected_row.kill()
                self.list_box.remove(selected_row)
                self.app.db.remove_by_id(app_id)
        confirmation.destroy()
        self.refresh_window()

    def save_window_state(self):
        """
            Save window position
        """
        x, y = self.get_position()
        self.app.cfg.update("position-x", x, "preferences")
        self.app.cfg.update("position-y", y, "preferences")

    def move_latest_position(self):
        """
            move the application window to the latest position
        """
        x = self.app.cfg.read("position-x", "preferences")
        y = self.app.cfg.read("position-y", "preferences")
        if x != 0 and y != 0:
            self.move(x, y)
        else:
            self.set_position(Gtk.WindowPosition.CENTER)
