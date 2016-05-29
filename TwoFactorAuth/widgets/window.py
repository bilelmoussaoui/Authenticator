from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gio, Gdk, GObject
from TwoFactorAuth.widgets.add_authenticator import AddAuthenticator
from TwoFactorAuth.widgets.confirmation import ConfirmationMessage
from TwoFactorAuth.widgets.listrow import ListBoxRow
from threading import Thread
import logging
from hashlib import md5
from gettext import gettext as _


class Window(Gtk.ApplicationWindow):
    app = None
    selected_app_idx = None
    selected_count = 0

    def __init__(self, application):
        self.app = application
        self.generate_window()
        self.generate_headerbar()
        self.generate_searchbar()
        self.generate_applications_list()
        if self.app.locked:
            self.generate_login_form()
        self.get_children()[0].get_children()[0].set_visible(False)

    def generate_window(self, *args):
        Gtk.ApplicationWindow.__init__(self, Gtk.WindowType.TOPLEVEL,
                                       application=self.app)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_wmclass(self.app.package, "TwoFactorAuth")
        self.resize(350, 500)
        self.set_size_request(350, 500)
        self.set_resizable(False)
        self.connect("key_press_event", self.on_key_press)
        self.connect("delete-event", lambda x, y: self.app.on_quit())
        self.add(Gtk.Box(orientation=Gtk.Orientation.VERTICAL))

    def on_key_press(self, app, keyevent):
        keypressed = Gdk.keyval_name(keyevent.keyval).lower()
        if not self.app.locked:
            CONTROL_MASK = Gdk.ModifierType.CONTROL_MASK
            search_box = self.get_children()[0].get_children()[
                0].get_children()[0]
            count = self.app.auth.count()
            if keypressed == "c":
                if keyevent.state == CONTROL_MASK:
                    self.copy_code()
            elif keypressed == "f":
                if keyevent.state == CONTROL_MASK:
                    self.toggle_searchobox()
            elif keypressed == "s":
                if keyevent.state == CONTROL_MASK:
                    self.toggle_select()
            elif keypressed == "n":
                if keyevent.state == CONTROL_MASK:
                    self.add_application()
            elif keypressed == "delete" and not search_box.get_visible():
                self.remove_application()
            elif keypressed == "return":
                if count > 0:
                    if self.listbox.get_selected_row():
                        index = self.listbox.get_selected_row().get_index()
                    else:
                        index = 0
                    listrow_box = self.listbox.get_row_at_index(index)
                    listbox = listrow_box.get_children()[0]
                    code_box = listbox.get_children()[1]
                    is_visible = code_box.get_no_show_all()
                    code_box.set_no_show_all(not is_visible)
                    code_box.set_visible(is_visible)
                    code_box.show_all()
            elif keypressed == "backspace":
                search_box = self.get_children()[0].get_children()[
                    0].get_children()[0]
                search_entry = search_box.get_children()[0]
                if len(search_entry.get_text()) == 0:
                    search_box.set_visible(False)
                    self.listbox.set_filter_func(lambda x, y, z: True, None,
                                                 False)
        else:
            if keypressed == "return":
                self.on_login_clicked()

    def filter_applications(self, entry):
        data = entry.get_text()
        if len(data) != 0:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY,
                                          "edit-clear-symbolic")
        else:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY,
                                          None)
        self.listbox.set_filter_func(self.filter_func, data, False)

    def generate_searchbar(self):
        hbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        search_entry = Gtk.Entry()
        search_box.set_margin_left(60)
        search_entry.set_width_chars(21)
        search_entry.connect("changed", self.filter_applications)
        search_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY,
                                             "system-search-symbolic")

        search_box.pack_start(search_entry, False, True, 0)
        hbox.pack_start(search_box, False, True, 6)
        self.get_children()[0].pack_start(hbox, True, True, 0)
        search_box.set_no_show_all(True)

    def remove_selected(self, *args):
        message = _("Do you really want to remove this application?")
        confirmation = ConfirmationMessage(self, message)
        confirmation.show()
        if confirmation.get_confirmation():
            for row in self.listbox.get_children():
                checkbox = self.get_checkbox_from_row(row)
                if checkbox.get_active():
                    label_id = row.get_children()[0].get_children()[2]
                    label_id = int(label_id.get_text())
                    self.app.auth.remove_by_id(label_id)
                    self.listbox.remove(row)
            self.listbox.unselect_all()
        confirmation.destroy()
        self.refresh_window()

    def generate_login_form(self):
        mainbox = self.get_children()[0]

        login_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        password_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        password_entry = Gtk.Entry()
        password_entry.set_visibility(False)
        password_entry.set_placeholder_text(_("Enter your password"))
        password_box.pack_start(password_entry, False, False, 6)

        login_button = Gtk.Button()
        login_button.set_label(_("Login"))
        login_button.connect("clicked", self.on_login_clicked)
        password_box.pack_start(login_button, False, False, 6)
        login_box.pack_start(password_box, True, False, 6)

        mainbox.pack_start(login_box, True, False, 0)
        mainbox.get_children()[0].set_no_show_all(self.app.locked)
        mainbox.get_children()[1].set_no_show_all(self.app.locked)
        mainbox.get_children()[2].set_no_show_all(not self.app.locked)
        self.hide_headerbar()

    def on_login_clicked(self, *args):
        login_box = self.get_children()[0].get_children()[2]
        entry = login_box.get_children()[0].get_children()[0]
        password = md5(entry.get_text().encode("utf-8")).hexdigest()
        if password == self.app.cfg.read("password", "login"):
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "")
            self.toggle_app_lock()
        else:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY,
                                          "dialog-error-symbolic")

    def toggle_app_lock(self):
        self.app.locked = not self.app.locked
        mainbox = self.get_children()[0]
        mainbox.get_children()[2].set_visible(self.app.locked)
        mainbox.get_children()[2].set_no_show_all(not self.app.locked)
        self.refresh_window()

    def hide_headerbar(self):
        hb = self.get_children()[1]
        hb.get_children()[0].get_children()[0].set_no_show_all(True)
        hb.get_children()[0].get_children()[1].set_no_show_all(True)
        hb.get_children()[1].get_children()[0].set_no_show_all(True)
        hb.get_children()[1].get_children()[1].set_no_show_all(True)
        hb.get_children()[1].get_children()[2].set_no_show_all(True)

    def generate_headerbar(self):
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)

        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(left_box.get_style_context(), "linked")
        Gtk.StyleContext.add_class(right_box.get_style_context(), "linked")
        self.remove_button = Gtk.Button()
        remove_icon = Gio.ThemedIcon(name="user-trash-symbolic")
        remove_image = Gtk.Image.new_from_gicon(remove_icon,
                                                Gtk.IconSize.BUTTON)
        self.remove_button.set_tooltip_text(_("Remove selected two factor auth "
                                              "sources"))
        self.remove_button.set_sensitive(False)
        self.remove_button.set_image(remove_image)
        self.remove_button.set_no_show_all(True)
        self.remove_button.connect("clicked", self.remove_selected)
        left_box.add(self.remove_button)

        add_button = Gtk.Button()
        add_icon = Gio.ThemedIcon(name="list-add-symbolic")
        add_image = Gtk.Image.new_from_gicon(add_icon,
                                             Gtk.IconSize.BUTTON)
        add_button.set_tooltip_text(_("Add a new application"))
        add_button.set_image(add_image)
        add_button.connect("clicked", self.add_application)
        left_box.add(add_button)

        select_button = Gtk.Button()
        select_icon = Gio.ThemedIcon(name="object-select-symbolic")
        select_image = Gtk.Image.new_from_gicon(select_icon,
                                                Gtk.IconSize.BUTTON)
        select_button.set_tooltip_text(_("Select mode"))
        select_button.set_image(select_image)
        select_button.connect("clicked", self.toggle_select)
        select_button.set_no_show_all(not self.app.auth.count() > 0)

        search_button = Gtk.ToggleButton()
        search_icon = Gio.ThemedIcon(name="system-search-symbolic")
        search_image = Gtk.Image.new_from_gicon(search_icon,
                                                Gtk.IconSize.BUTTON)
        search_button.set_tooltip_text(_("Search"))
        search_button.set_image(search_image)
        search_button.connect("clicked", self.toggle_searchobox)
        search_button.set_no_show_all(not self.app.auth.count() > 0)

        cancel_buton = Gtk.Button()
        cancel_buton.set_label(_("Cancel"))
        cancel_buton.connect("clicked", self.toggle_select)
        cancel_buton.set_no_show_all(True)

        right_box.add(search_button)
        right_box.add(select_button)
        right_box.add(cancel_buton)

        hb.pack_start(left_box)
        hb.pack_end(right_box)
        self.set_titlebar(hb)

    def add_application(self, *args):
        AddAuthenticator(self)

    def toggle_searchobox(self, *args):
        if self.app.auth.count() > 0:
            search_box = self.get_children()[0].get_children()[
                0].get_children()[0]
            is_visible = search_box.get_no_show_all()

            headerbar = self.get_children()[1]
            search_button = headerbar.get_children()[1].get_children()[0]
            search_box.set_no_show_all(not is_visible)
            search_box.set_visible(is_visible)
            search_box.show_all()
            if is_visible:
                search_button.get_style_context().add_class("toggle")
                search_box.get_children()[0].grab_focus_without_selecting()
            else:
                search_button.get_style_context().remove_class("toggle")
                self.listbox.set_filter_func(lambda x, y, z: True, None, False)

    def toggle_select(self, *args):
        i = 0
        button_visible = self.remove_button.get_visible()
        headerbar = self.get_children()[1]
        headerbar.set_show_close_button(button_visible)
        headerbar.get_children()[0].get_children()[
            1].set_visible(button_visible)
        headerbar.get_children()[1].get_children()[
            1].set_visible(button_visible)
        headerbar.get_children()[1].get_children()[
            2].set_visible(not button_visible)
        self.remove_button.set_visible(not button_visible)
        self.remove_button.set_no_show_all(button_visible)

        if not button_visible:
            self.listbox.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
            headerbar.get_style_context().add_class("selection-mode")
        else:
            self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
            headerbar.get_style_context().remove_class("selection-mode")

            if self.selected_app_idx:
                index = self.selected_app_idx
            else:
                index = 0
            listrow_box = self.listbox.get_row_at_index(index)
            self.listbox.select_row(listrow_box)

        for row in self.listbox.get_children():
            checkbox = self.get_checkbox_from_row(row)
            visible = checkbox.get_visible()
            selected = checkbox.get_active()
            if not button_visible:
                self.select_application(checkbox)
            checkbox.set_visible(not visible)
            checkbox.set_no_show_all(visible)

    def select_application(self, checkbutton):
        is_active = checkbutton.get_active()
        listbox_row = checkbutton.get_parent().get_parent().get_parent()
        if is_active:
            self.listbox.select_row(listbox_row)
            self.selected_count += 1
        else:
            self.listbox.unselect_row(listbox_row)
            self.selected_count -= 1
        self.remove_button.set_sensitive(self.selected_count > 0)

    def filter_func(self, row, data, notify_destroy):
        app_label = row.get_children()[0].get_children()[0].get_children()
        data = data.strip()
        if len(data) > 0:
            return data in app_label[2].get_children()[0].get_text().lower()
        else:
            return True

    def get_checkbox_from_row(self, row):
        if row:
            return row.get_children()[0].get_children()[0].get_children()[0]
        else:
            return None

    def select_row(self, listbox, listbox_row):
        index = listbox_row.get_index()
        button_visible = self.remove_button.get_visible()
        checkbox = self.get_checkbox_from_row(listbox_row)
        if button_visible:
            checkbox.set_active(not checkbox.get_active())
        else:
            if self.selected_app_idx:
                listrow_box = self.listbox.get_row_at_index(
                    self.selected_app_idx)
                self.listbox.unselect_row(listbox_row)
            self.selected_app_idx = index
            listrow_box = self.listbox.get_row_at_index(index)
            self.listbox.select_row(listbox_row)

    # TODO : show a nice message when no application is added
    def generate_applications_list(self):
        list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        count = self.app.auth.count()
        # Create a ScrolledWindow for installed applications
        self.listbox = Gtk.ListBox()
        self.listbox.get_style_context().add_class("applications-list")
        self.listbox.set_adjustment()
        self.listbox.connect("row_activated", self.select_row)
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        list_box.pack_start(self.listbox, True, True, 0)

        scrolled_win = Gtk.ScrolledWindow()
        scrolled_win.add_with_viewport(list_box)
        self.get_children()[0].get_children()[0].pack_start(
            scrolled_win, True, True, 0)

        apps = self.app.auth.fetch_apps()
        i = 0
        count = len(apps)
        while i < count:
            row = ListBoxRow(self, apps[i][0], apps[i][1], apps[i][2],
                             apps[i][3])
            self.listbox.add(row.get_listrow())
            i += 1

        nolist_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        logo_image = Gtk.Image()
        logo_image.set_from_icon_name("dialog-information-symbolic",
                                      Gtk.IconSize.DIALOG)
        vbox.pack_start(logo_image, False, False, 6)

        no_proivders_label = Gtk.Label()
        no_proivders_label.set_text(_("There's no application at the moment"))
        vbox.pack_start(no_proivders_label, False, False, 6)

        nolist_box.pack_start(vbox, True, True, 0)
        self.get_children()[0].pack_start(nolist_box, True, True, 0)
        self.get_children()[0].get_children()[0].set_no_show_all(count == 0)
        self.get_children()[0].get_children()[
            1].set_no_show_all(not count == 0)

    def update_list(self, id, name, secret_code, image):
        row = ListBoxRow(self, id, name, secret_code, image)
        self.listbox.add(row.get_listrow())
        self.listbox.show_all()

    def copy_code(self, *args):
        if len(args) > 0:
            row = args[0].get_parent().get_parent().get_parent()
            self.listbox.select_row(row)
        selected_row = self.listbox.get_selected_row()
        label = selected_row.get_children()[0].get_children()[1].get_children()
        code = label[0].get_text()
        try:
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            clipboard.clear()
            clipboard.set_text(code, len(code))
            logging.debug("Secret code copied to clipboard")
        except Exception as e:
            logging.error(str(e))

    def refresh_window(self):
        mainbox = self.get_children()[0]
        count = self.app.auth.count()
        headerbar = self.get_children()[1]
        if count == 0:
            mainbox.get_children()[0].set_visible(False)
            mainbox.get_children()[1].set_visible(True)
            mainbox.get_children()[1].set_no_show_all(False)
            mainbox.get_children()[1].show_all()
            headerbar.get_children()[0].get_children()[1].set_visible(True)
            headerbar.get_children()[1].get_children()[1].set_visible(False)
            headerbar.get_children()[1].get_children()[2].set_visible(False)
            headerbar.set_show_close_button(True)
            headerbar.get_style_context().remove_class("selection-mode")
        else:
            self.get_children()[0].get_children()[0].set_no_show_all(False)
            self.get_children()[0].get_children()[0].set_visible(True)
            self.get_children()[0].get_children()[0].show_all()
            headerbar.get_children()[0].get_children()[0].set_visible(False)
            headerbar.get_children()[1].get_children()[0].set_visible(True)
            headerbar.get_children()[1].get_children()[1].set_visible(True)
            mainbox.get_children()[1].set_visible(False)

        headerbar.get_children()[0].get_children()[1].set_no_show_all(False)
        headerbar.get_children()[0].get_children()[1].set_visible(True)

        headerbar = self.get_children()[1]
        left_box = headerbar.get_children()[0]
        right_box = headerbar.get_children()[1]
        right_box.get_children()[0].set_visible(count > 0)
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        left_box.get_children()[0].set_visible(False)

    def remove_application(self, *args):
        if len(args) > 0:
            row = args[0].get_parent().get_parent().get_parent()
            self.listbox.select_row(row)

        message = _("Do you really want to remove the application?")
        confirmation = ConfirmationMessage(self, message)
        confirmation.show()
        if confirmation.get_confirmation():
            if self.listbox.get_selected_row():
                selected_row = self.listbox.get_selected_row()
                self.listbox.remove(selected_row)
                label_id = selected_row.get_children()[0].get_children()[2]
                self.app.auth.remove_by_id(int(label_id.get_text()))
        confirmation.destroy()
        self.refresh_window()

    def show_about(self, *args):
        builder = Gtk.Builder()
        builder.add_from_file(self.app.pkgdatadir + "/data/about.ui")

        dialog = builder.get_object("AboutDialog")
        dialog.set_transient_for(self)
        dialog.run()
        dialog.destroy()

    def show_shortcuts(self, *args):
        builder = Gtk.Builder()
        builder.add_from_file(self.app.pkgdatadir + "/data/shortcuts.ui")

        shortcuts = builder.get_object("shortcuts")
        shortcuts.set_transient_for(self)
        shortcuts.show()
