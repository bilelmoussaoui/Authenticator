
from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gio, Gdk, GObject
from TwoFactorAuth.ui.add_provider import AddProviderWindow
from TwoFactorAuth.ui.confirmation import ConfirmationMessage
from TwoFactorAuth.ui.listrow import ListBoxRow
from threading import Thread

import logging
from math import pi
logging.basicConfig(level=logging.DEBUG,
                format='[%(levelname)s] %(message)s',
                )

class Window(Gtk.ApplicationWindow):
    app = None
    selected_app_idx = None

    def __init__(self, application):
        self.app = application
        self.generate_window()
        self.generate_headerbar()
        self.genereate_searchbar()
        self.generate_applications_list()
        self.get_children()[0].get_children()[0].set_visible(False)

    def generate_window(self, *args):
        Gtk.ApplicationWindow.__init__(self, Gtk.WindowType.TOPLEVEL,
                                    application=self.app)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_wmclass("two_factor_auth", "Two-Factor Auth")
        self.resize(350, 500)
        self.set_size_request(350, 500)
        self.set_resizable(False)
        self.connect("key_press_event", self.on_key_press)
        self.app.win = self
        self.connect("delete-event", lambda x, y: self.app.on_quit())
        self.add(Gtk.Box(orientation=Gtk.Orientation.VERTICAL))

    def on_key_press(self, provider, keyevent):
        CONTROL_MASK = Gdk.ModifierType.CONTROL_MASK
        search_box = self.get_children()[0].get_children()[0].get_children()[0]

        keypressed = Gdk.keyval_name(keyevent.keyval).lower()
        if keypressed == "c":
            if keyevent.state == CONTROL_MASK:
                self.copy_code()
        elif keypressed == "f":
            if keyevent.state == CONTROL_MASK:
                if self.app.provider.count_providers() > 0:
                    is_visible = search_box.get_no_show_all()
                    search_box.set_no_show_all(not is_visible)
                    search_box.set_visible(is_visible)
                    search_box.show_all()
                    if is_visible:
                        search_box.get_children()[0].grab_focus_without_selecting()
                    else:
                        self.listbox.set_filter_func(lambda x,y,z : True, None, False)
        elif keypressed == "n":
            if keyevent.state == CONTROL_MASK:
                self.add_provider()
        elif keypressed == "delete" and not search_box.get_visible():
            self.remove_provider()
        elif keypressed == "return":
            if self.app.provider.count_providers() > 0:
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

    def filter_providers(self, entry):
        data = entry.get_text()
        if len(data) != 0:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY,
                                                "edit-clear-symbolic")
        else:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY,
                                            None)
        self.listbox.set_filter_func(self.filter_func, data, False)

    def genereate_searchbar(self):
        hbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        search_entry = Gtk.Entry()
        search_box.set_margin_left(60)
        search_entry.set_width_chars(21)
        search_entry.connect("changed", self.filter_providers)
        search_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY,
                                            "system-search-symbolic")

        search_box.pack_start(search_entry, False, True, 0)
        hbox.pack_start(search_box, False, True, 6)
        self.get_children()[0].pack_start(hbox, True, True, 0)
        search_box.set_no_show_all(True)

    def remove_selected(self, *args):
        message = "Do you really want to remove the two-factor auth provider?"
        confirmation = ConfirmationMessage(self, message)
        confirmation.show()
        if confirmation.get_confirmation():
            for row in self.listbox.get_children():
                checkbox = self.get_checkbox_from_row(row)
                if checkbox.get_active():
                    label_id = row.get_children()[0].get_children()[2]
                    label_id = int(label_id.get_text())
                    self.app.provider.remove_from_database(label_id)
                    self.listbox.remove(row)
            self.listbox.unselect_all()
        confirmation.destroy()
        self.refresh_window()


    def generate_headerbar(self):
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)

        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(left_box.get_style_context(), "linked")
        Gtk.StyleContext.add_class(right_box.get_style_context(), "linked")
        self.remove_button = Gtk.Button()
        remove_icon = Gio.ThemedIcon(name="list-remove-symbolic")
        remove_image = Gtk.Image.new_from_gicon(remove_icon,
                                                Gtk.IconSize.BUTTON)
        self.remove_button.set_tooltip_text("Remove selected two factor auth "
                                            "sources")

        self.remove_button.set_image(remove_image)
        self.remove_button.set_no_show_all(True)
        self.remove_button.connect("clicked", self.remove_selected)
        left_box.add(self.remove_button)

        add_button = Gtk.Button()
        add_icon = Gio.ThemedIcon(name="list-add-symbolic")
        add_image = Gtk.Image.new_from_gicon(add_icon,
                                             Gtk.IconSize.BUTTON)
        add_button.set_tooltip_text("Add a new Two factor website")
        add_button.set_image(add_image)
        add_button.connect("clicked", self.add_provider)
        left_box.add(add_button)

        select_button = Gtk.Button()
        select_icon = Gio.ThemedIcon(name="object-select-symbolic")
        select_image = Gtk.Image.new_from_gicon(select_icon,
                                                Gtk.IconSize.BUTTON)
        select_button.set_tooltip_text("Select mode")
        select_button.set_image(select_image)
        select_button.connect("clicked", self.show_checkbox)
        select_button.set_no_show_all(not self.app.provider.count_providers() > 0)

        right_box.add(select_button)
        hb.pack_start(left_box)
        hb.pack_end(right_box)
        self.set_titlebar(hb)

    def add_provider(self, *args):
        AddProviderWindow(self)

    def show_checkbox(self, *args):
        i = 0
        button_visible = self.remove_button.get_visible()

        self.remove_button.set_visible(not button_visible)
        self.remove_button.set_no_show_all(button_visible)

        if not button_visible:
            self.listbox.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        else:
            self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
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
        else:
            self.listbox.unselect_row(listbox_row)

    def filter_func(self, row, data, notify_destroy):
        provider_label = row.get_children()[0].get_children()[0].get_children()
        data = data.strip()
        if len(data) > 0:
            return data in provider_label[2].get_text().lower()
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
        count = self.app.provider.count_providers()
        # Create a ScrolledWindow for installed applications
        self.listbox = Gtk.ListBox()
        self.listbox.get_style_context().add_class("applications-list")
        self.listbox.set_adjustment()
        self.listbox.connect("row_activated", self.select_row)
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        list_box.pack_start(self.listbox, True, True, 0)

        scrolled_win = Gtk.ScrolledWindow()
        scrolled_win.add_with_viewport(list_box)
        self.get_children()[0].get_children()[0].pack_start(scrolled_win, True, True, 0)

        providers =  self.app.provider.fetch_providers()
        i = 0
        while i < len(providers):
            row = ListBoxRow(self, providers[i][0], providers[i][1],
                                    providers[i][2], providers[i][3])
            self.listbox.add(row.get_listrow())
            i += 1

        nolist_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        logo_image = Gtk.Image()
        logo_image.set_from_icon_name("dialog-information-symbolic",
                                       Gtk.IconSize.DIALOG)
        vbox.pack_start(logo_image, False, False, 6)

        no_proivders_label = Gtk.Label()
        no_proivders_label.set_text("There's no providers at the moment")
        vbox.pack_start(no_proivders_label, False, False, 6)

        nolist_box.pack_start(vbox, True, True, 0)
        self.get_children()[0].pack_start(nolist_box, True, True, 0)
        self.get_children()[0].get_children()[0].set_no_show_all(len(providers) == 0)
        self.get_children()[0].get_children()[1].set_no_show_all(not len(providers) == 0)


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
        except Exception as e:
            logging.error(str(e))

    def refresh_window(self):
        mainbox = self.get_children()[0]
        count = self.app.provider.count_providers()
        if count == 0:
            mainbox.get_children()[0].set_visible(False)
            mainbox.get_children()[1].set_visible(True)
            mainbox.get_children()[1].set_no_show_all(False)
            mainbox.get_children()[1].show_all()
        else:
            mainbox.get_children()[0].set_visible(True)
            mainbox.get_children()[0].show_all()
            self.listbox.show_all()
            mainbox.get_children()[1].set_visible(False)
        headerbar = self.get_children()[1]
        left_box = headerbar.get_children()[0]
        right_box = headerbar.get_children()[1]
        right_box.get_children()[0].set_visible(count > 0)
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        left_box.get_children()[0].set_visible(False)



    def remove_provider(self, *args):
        if len(args) > 0:
            row = args[0].get_parent().get_parent().get_parent()
            self.listbox.select_row(row)

        message = "Do you really want to remove the two-factor auth provider?"
        confirmation = ConfirmationMessage(self, message)
        confirmation.show()
        if confirmation.get_confirmation():
            if self.listbox.get_selected_row():
                selected_row = self.listbox.get_selected_row()
                self.listbox.remove(selected_row)
                label_id = selected_row.get_children()[0].get_children()[2]
                self.app.provider.remove_from_database(int(label_id.get_text()))
        confirmation.destroy()
        self.refresh_window()


    def show_about(self, *args):
        builder = Gtk.Builder()
        builder.add_from_file("/home/bilal/Projects/Two-factor-gtk/data/about.glade")

        dialog = builder.get_object("AboutDialog")
        dialog.set_transient_for(self)
        dialog.run()
        dialog.destroy()

    def show_shortcuts(self, *args):
        builder = Gtk.Builder()
        builder.add_from_file("/home/bilal/Projects/Two-factor-gtk/data/shortcuts.glade")

        shortcuts = builder.get_object("shortcuts")
        shortcuts.set_transient_for(self)
        shortcuts.show()

    def show(self):
        self.show_all()
        Gtk.main()
