from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, Gdk
from TwoFactorAuth.widgets.add_authenticator import AddAuthenticator
from TwoFactorAuth.widgets.confirmation import ConfirmationMessage
from TwoFactorAuth.widgets.listrow import ListBoxRow
import logging
from hashlib import md5
from gettext import gettext as _


class Window(Gtk.ApplicationWindow):
    app = None
    selected_app_idx = None
    selected_count = 0

    hb = Gtk.HeaderBar()
    main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    search_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    login_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    no_apps_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    apps_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    apps_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

    list_box = Gtk.ListBox()
    search_button = Gtk.ToggleButton()
    add_button = Gtk.Button()
    remove_button = Gtk.Button()
    cancel_button = Gtk.Button()
    select_button = Gtk.Button()

    password_entry = Gtk.Entry()
    search_entry = Gtk.Entry()

    def __init__(self, application):
        self.app = application
        self.generate_window()
        self.generate_header_bar()
        self.generate_search_bar()
        self.generate_applications_list()
        self.generate_no_apps_box()
        self.generate_login_form()
        self.refresh_window()

    def generate_window(self, *args):
        """
            Generate application window (Gtk.Window)
        """
        Gtk.ApplicationWindow.__init__(self, Gtk.WindowType.TOPLEVEL,
                                       application=self.app)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_wmclass(self.app.package, "TwoFactorAuth")
        self.resize(380, 500)
        self.set_size_request(380, 500)
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
            count = self.app.auth.count()
            if keypress == "c":
                if key_event.state == control_mask:
                    self.copy_code()
            elif keypress == "f":
                if key_event.state == control_mask:
                    self.toggle_search_box()

            elif keypress == "s":
                if key_event.state == control_mask:
                    self.toggle_select()
            elif keypress == "n":
                if key_event.state == control_mask:
                    self.add_application()
            elif keypress == "delete" and not self.search_box.get_visible():
                self.remove_application()
            elif keypress == "return":
                if count > 0:
                    if self.list_box.get_selected_row():
                        index = self.list_box.get_selected_row().get_index()
                    else:
                        index = 0
                    ListBoxRow.toggle_code_box(self.list_box.get_row_at_index(index))
            elif keypress == "backspace":
                if len(self.search_entry.get_text()) == 0:
                    self.toggle_search_box()
            elif keypress == "escape":
                if self.search_box.get_no_show_all():
                    self.toggle_search_box()
        else:
            if keypress == "return":
                self.on_unlock_clicked()

    def filter_applications(self, entry):
        data = entry.get_text().strip()
        if len(data) != 0:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "edit-clear-symbolic")
        else:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, None)
        self.list_box.set_filter_func(self.filter_func, data, False)

    def generate_search_bar(self):
        """
            Generate search bar box and entry
        """
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.set_margin_left(60)

        self.search_entry.set_width_chars(22)
        self.search_entry.connect("changed", self.filter_applications)
        self.search_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, "system-search-symbolic")

        box.pack_start(self.search_entry, False, True, 0)
        self.search_box.pack_start(box, False, True, 6)
        self.search_box.set_no_show_all(True)
        self.apps_box.pack_start(self.search_box, False, True, 0)
        self.main_box.pack_start(self.apps_box, True, True, 0)

    def remove_selected(self, *args):
        """
            Remove selected applications
        """
        message = _("Do you really want to remove selected applications?")
        confirmation = ConfirmationMessage(self, message)
        confirmation.show()
        if confirmation.get_confirmation():
            for row in self.list_box.get_children():
                checkbox = ListBoxRow.get_checkbox(row)
                if checkbox.get_active():
                    label_id = ListBoxRow.get_id(row)
                    self.app.auth.remove_by_id(label_id)
                    self.list_box.remove(row)
            self.list_box.unselect_all()
        confirmation.destroy()
        self.refresh_window()

    def generate_login_form(self):
        """
            Generate login form
        """
        password_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.password_entry.set_visibility(False)
        self.password_entry.set_placeholder_text(_("Enter your password"))
        password_box.pack_start(self.password_entry, False, False, 6)

        unlock_button = Gtk.Button()
        unlock_button.set_label(_("Unlock"))
        unlock_button.connect("clicked", self.on_unlock_clicked)

        password_box.pack_start(unlock_button, False, False, 6)
        self.login_box.pack_start(password_box, True, False, 6)

        self.main_box.pack_start(self.login_box, True, False, 0)

    def on_unlock_clicked(self, *args):
        """
            Password check and unlock
        """
        password = self.password_entry.get_text()
        password = md5(password.encode("utf-8")).hexdigest()
        if password == self.app.cfg.read("password", "login"):
            self.password_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, None)
            self.toggle_app_lock()
            self.app.locked = False
            self.app.toggle_settings_menu()
            self.password_entry.set_text("")
            self.app.refresh_menu()
        else:
            self.password_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "dialog-error-symbolic")

    def toggle_app_lock(self):
        """
            Lock/unlock the application
        """
        self.app.locked = not self.app.locked
        self.app.refresh_menu()
        self.refresh_window()

    def toggle_boxes(self, apps_box, no_apps_box, login_box):
        """
            Change the status of all the boxes in one time
            :param apps_box: bool
            :param no_apps_box: bool
            :param login_box: bool
            :return:
        """
        self.login_box.set_visible(login_box)
        self.login_box.set_no_show_all(not login_box)
        self.apps_box.set_visible(apps_box)
        self.apps_box.set_no_show_all(not apps_box)
        self.no_apps_box.set_visible(no_apps_box)
        self.no_apps_box.set_no_show_all(not no_apps_box)

    def hide_header_bar(self):
        """
            Hide all buttons on the header bar
        """
        self.toggle_hb_buttons(False, False, False, False, False)

    def generate_header_bar(self):
        """
            Generate a header bar box
        """
        self.hb.set_show_close_button(True)

        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        remove_icon = Gio.ThemedIcon(name="user-trash-symbolic")
        remove_image = Gtk.Image.new_from_gicon(remove_icon, Gtk.IconSize.BUTTON)
        self.remove_button.set_tooltip_text(_("Remove selected two factor auth sources"))
        self.remove_button.set_image(remove_image)
        self.remove_button.set_sensitive(False)
        self.remove_button.set_no_show_all(True)
        self.remove_button.connect("clicked", self.remove_selected)

        add_icon = Gio.ThemedIcon(name="list-add-symbolic")
        add_image = Gtk.Image.new_from_gicon(add_icon, Gtk.IconSize.BUTTON)
        self.add_button.set_tooltip_text(_("Add a new application"))
        self.add_button.set_image(add_image)
        self.add_button.connect("clicked", self.add_application)

        left_box.add(self.remove_button)
        left_box.add(self.add_button)

        select_icon = Gio.ThemedIcon(name="object-select-symbolic")
        select_image = Gtk.Image.new_from_gicon(select_icon, Gtk.IconSize.BUTTON)
        self.select_button.set_tooltip_text(_("Select mode"))
        self.select_button.set_image(select_image)
        self.select_button.connect("clicked", self.toggle_select)
        self.select_button.set_no_show_all(not self.app.auth.count() > 0)

        search_icon = Gio.ThemedIcon(name="system-search-symbolic")
        search_image = Gtk.Image.new_from_gicon(search_icon, Gtk.IconSize.BUTTON)
        self.search_button.set_tooltip_text(_("Search"))
        self.search_button.set_image(search_image)
        self.search_button.connect("clicked", self.toggle_search_box)
        self.search_button.set_no_show_all(not self.app.auth.count() > 0)

        self.cancel_button.set_label(_("Cancel"))
        self.cancel_button.connect("clicked", self.toggle_select)
        self.cancel_button.set_no_show_all(True)

        right_box.add(self.search_button)
        right_box.add(self.select_button)
        right_box.add(self.cancel_button)

        self.hb.pack_start(left_box)
        self.hb.pack_end(right_box)
        self.set_titlebar(self.hb)

    def add_application(self, *args):
        """
            Create add application window
        """
        AddAuthenticator(self)

    def toggle_search_box(self, *args):
        """
            Toggle search box, only if there's an application
        """
        if self.app.auth.count() > 0:
            is_visible = self.search_box.get_no_show_all()
            self.search_box.set_no_show_all(not is_visible)
            self.search_box.set_visible(is_visible)
            self.search_box.show_all()

            if is_visible:
                self.search_entry.grab_focus_without_selecting()
            else:
                self.list_box.set_filter_func(lambda x, y, z: True, None, False)

    def toggle_select(self, *args):
        """
            Toggle select mode
        """
        is_visible = self.remove_button.get_visible()

        self.remove_button.set_visible(not is_visible)
        self.remove_button.set_no_show_all(is_visible)

        self.hb.set_show_close_button(is_visible)
        self.cancel_button.set_visible(not is_visible)
        self.remove_button.set_visible(not is_visible)
        self.add_button.set_visible(is_visible)
        self.select_button.set_visible(is_visible)

        if not is_visible:
            self.list_box.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
            self.hb.get_style_context().add_class("selection-mode")
        else:
            self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
            self.hb.get_style_context().remove_class("selection-mode")

            if self.selected_app_idx:
                index = self.selected_app_idx
            else:
                index = 0
            list_row_box = self.list_box.get_row_at_index(index)
            self.list_box.select_row(list_row_box)

        for row in self.list_box.get_children():
            checkbox = ListBoxRow.get_checkbox(row)
            visible = checkbox.get_visible()
            selected = checkbox.get_active()
            if not is_visible:
                self.select_application(checkbox)
            checkbox.set_visible(not visible)
            checkbox.set_no_show_all(visible)

    def select_application(self, checkbutton):
        """
            Select an application in the application ListBox
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
        self.remove_button.set_sensitive(self.selected_count > 0)

    def filter_func(self, row, data, notify_destroy):
        """
            Filter function, used to check if the entered data exists on the application ListBox
        """
        app_label = ListBoxRow.get_label(row)
        data = data.lower()
        if len(data) > 0:
            return data in app_label.lower()
        else:
            return True

    def select_row(self, list_box, listbox_row):
        """
            Select row @override the clicked event by default for ListBoxRow
        """
        index = listbox_row.get_index()
        button_visible = self.remove_button.get_visible()
        checkbox = ListBoxRow.get_checkbox(listbox_row)
        if button_visible:
            checkbox.set_active(not checkbox.get_active())
        else:
            if self.selected_app_idx:
                selected_row = self.list_box.get_row_at_index(self.selected_app_idx)
                if selected_row:
                    self.list_box.unselect_row(selected_row)
            self.selected_app_idx = index
            self.list_box.select_row(self.list_box.get_row_at_index(index))

    def generate_applications_list(self):
        """
            Generate an application ListBox inside of a ScrolledWindow
        """
        count = self.app.auth.count()

        # Create a ScrolledWindow for installed applications
        self.list_box.get_style_context().add_class("applications-list")
        self.list_box.set_adjustment()
        self.list_box.connect("row_activated", self.select_row)
        self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.apps_list_box.pack_start(self.list_box, True, True, 0)

        scrolled_win = Gtk.ScrolledWindow()
        scrolled_win.add_with_viewport(self.apps_list_box)
        self.apps_box.pack_start(scrolled_win, True, True, 0)

        apps = self.app.auth.fetch_apps()
        i = 0
        count = len(apps)
        while i < count:
            row = ListBoxRow(self, apps[i][0], apps[i][1], apps[i][2],
                             apps[i][3])
            self.list_box.add(row.get_list_row())
            i += 1

    def generate_no_apps_box(self):
        """
            Generate a box with no applications message
        """
        logo_image = Gtk.Image()
        logo_image.set_from_icon_name("dialog-information-symbolic",
                                      Gtk.IconSize.DIALOG)

        no_apps_label = Gtk.Label()
        no_apps_label.set_text(_("There's no application at the moment"))

        self.no_apps_box.pack_start(logo_image, False, False, 6)
        self.no_apps_box.pack_start(no_apps_label, False, False, 6)
        self.main_box.pack_start(self.no_apps_box, True, False, 0)

    def append_list_box(self, uid, name, secret_code, image):
        """
            Add an element to the ListBox
            :param uid: application id
            :param name: application name
            :param secret_code: application secret code
            :param image: application image path or icon name
        """
        row = ListBoxRow(self, uid, name, secret_code, image)
        self.list_box.add(row.get_list_row())
        self.list_box.show_all()

    def copy_code(self, *args):
        """
            Copy the secret code to clipboard
        """
        if len(args) > 0:
            # if the code is called by clicking on copy button, select the right ListBowRow
            row = args[0].get_parent().get_parent().get_parent()
            self.list_box.select_row(row)
        selected_row = self.list_box.get_selected_row()
        code = ListBoxRow.get_code(selected_row)
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
        count = self.app.auth.count()
        is_locked = self.app.locked

        if is_locked:
            self.toggle_boxes(False, False, True)
            self.hide_header_bar()
        else:
            if count == 0:
                self.toggle_boxes(False, True, False)
                self.toggle_hb_buttons(False, True, False, False, False)
            else:
                self.toggle_boxes(True, False, False)
                self.toggle_hb_buttons(False, True, True, True, False)

        self.main_box.show_all()
        self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)

    def toggle_hb_buttons(self, remove, add, search, select, cancel):
        """
            Toggle header bar buttons visibilty
            :param remove: (bool)
            :param add: (bool)
            :param search: (bool)
            :param select: (bool)
            :param cancel: (bool)
        """
        self.add_button.set_visible(add)
        self.add_button.set_no_show_all(not add)
        self.remove_button.set_visible(remove)
        self.remove_button.set_no_show_all(not remove)
        self.cancel_button.set_visible(cancel)
        self.cancel_button.set_no_show_all(not cancel)
        self.select_button.set_visible(select)
        self.select_button.set_no_show_all(not select)
        self.search_button.set_visible(search)
        self.search_button.set_no_show_all(not search)

    def remove_application(self, *args):
        """
            Remove an application
        """
        if len(args) > 0:
            row = args[0].get_parent().get_parent().get_parent()
            self.list_box.select_row(row)

        message = _("Do you really want to remove the application?")
        confirmation = ConfirmationMessage(self, message)
        confirmation.show()
        if confirmation.get_confirmation():
            if self.list_box.get_selected_row():
                selected_row = self.list_box.get_selected_row()
                app_id = ListBoxRow.get_id(selected_row)
                self.list_box.remove(selected_row)
                self.app.auth.remove_by_id(app_id)
        confirmation.destroy()
        self.refresh_window()

    def show_about(self, *args):
        """
            Shows about dialog
        """
        builder = Gtk.Builder()
        builder.add_from_file(self.app.pkgdatadir + "/data/about.ui")

        dialog = builder.get_object("AboutDialog")
        dialog.set_transient_for(self)
        dialog.run()
        dialog.destroy()

    def show_shortcuts(self, *args):
        """
            Shows keyboard shortcuts
        """
        if Gtk.get_major_version() >= 3 and Gtk.get_minor_version() >= 20:
            builder = Gtk.Builder()
            builder.add_from_file(self.app.pkgdatadir + "/data/shortcuts.ui")

            shortcuts = builder.get_object("shortcuts")
            shortcuts.set_transient_for(self)
            shortcuts.show()
