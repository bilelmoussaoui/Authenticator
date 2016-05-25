
from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gio, Gdk
from ui.add_provider import AddProviderWindow
from ui.confirmation import ConfirmationMessage
import logging

logging.basicConfig(level=logging.DEBUG,
                format='[%(levelname)s] %(message)s',
                )

class TwoFactorWindow(Gtk.Window):
    app = None
    selected_app_idx = None
    checkboxes = []

    def __init__(self, application):
        self.app = application
        self.generate_window()
        self.generate_headerbar()
        self.genereate_searchbar()
        self.generate_applications_list()
        self.get_children()[0].get_children()[0].set_visible(False)

    def generate_window(self, *args):
        Gtk.Window.__init__(self, application=self.app)
        self.connect("delete-event", lambda x, y: self.app.quit())
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_wmclass("twofactor", "Two-Factor")
        self.resize(350, 500)
        self.set_size_request(350, 500)
        self.set_resizable(False)
        self.connect("key_press_event", self.on_key_press)
        self.app.win = self
        self.add(Gtk.Box(orientation=Gtk.Orientation.VERTICAL))

    def on_key_press(self, provider, keyevent):
        CONTROL_MASK = Gdk.ModifierType.CONTROL_MASK
        keypressed = Gdk.keyval_name(keyevent.keyval).lower()
        if keypressed == "c":
            if keyevent.state == CONTROL_MASK:
                self.copy_code()
        elif keypressed == "f":
            if keyevent.state == CONTROL_MASK:
                if self.app.provider.count_providers() > 0:
                    search_box = self.get_children()[0].get_children()[0]
                    is_visible = search_box.get_no_show_all()
                    search_box.set_no_show_all(not is_visible)
                    search_box.set_visible(is_visible)
                    search_box.show_all()
                    if is_visible:
                        search_box.get_children()[1].grab_focus_without_selecting()
                    else:
                        self.listbox.set_filter_func(lambda x,y,z : True, None, False)
        elif keypressed == "delete":
            self.remove_application()
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
        self.listbox.set_filter_func(self.filter_func, data, False)

    def genereate_searchbar(self):
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hbox.set_margin_left(40)

        search_image = Gtk.Image(xalign=0)
        search_image.set_from_icon_name("system-search-symbolic",
                                       Gtk.IconSize.SMALL_TOOLBAR)
        search_image.set_tooltip_text("Type to search")

        search_entry = Gtk.Entry()
        search_entry.connect("changed", self.filter_providers)

        hbox.pack_start(search_image, False, True, 6)
        hbox.pack_start(search_entry, False, True, 6)
        hbox.set_visible(False)
        self.get_children()[0].pack_start(hbox, False, True, 6)
        self.get_children()[0].get_children()[0].set_no_show_all(True)


    def remove_selected(self, *args):
        i = 0
        confirmation = ConfirmationMessage(self, "Are you sure??")
        confirmation.show()
        if confirmation.get_confirmation():
            while i < len(self.checkboxes):
                if self.checkboxes[i].get_active():
                    selected_row = self.listbox.get_row_at_index(i)
                    label_id = selected_row.get_children()[0].get_children()[2]
                    self.app.provider.remove_from_database(int(label_id.get_text()))
                    self.listbox.remove(selected_row)
                    del self.checkboxes[i]
                i += 1
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

        while i < len(self.checkboxes):
            visible = self.checkboxes[i].get_visible()
            selected = self.checkboxes[i].get_active()
            if not button_visible:
                self.select_application(self.checkboxes[i])
            self.checkboxes[i].set_visible(not visible)
            self.checkboxes[i].set_no_show_all(visible)
            i += 1

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


    def select_row(self, listbox, listbox_row):
        index = listbox_row.get_index()
        button_visible = self.remove_button.get_visible()

        if self.checkboxes[index]:
            if button_visible:
                clicked = self.checkboxes[index].get_active()
                self.checkboxes[index].set_active(not clicked)
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
        box_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        count = self.app.provider.count_providers()
        if count > 0:
            # Create a ScrolledWindow for installed applications
            scrolled_win = Gtk.ScrolledWindow()
            scrolled_win.add_with_viewport(box_outer)
            self.get_children()[0].pack_start(scrolled_win, True, True, 0)

            self.listbox = Gtk.ListBox()
            self.listbox.get_style_context().add_class("applications-list")
            self.listbox.set_adjustment()
            self.listbox.connect("row_activated", self.select_row)
            self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
            box_outer.pack_start(self.listbox, True, True, 0)
            providers =  self.app.provider.fetch_providers()
            i = 0
            while i < count:
                row = self.generate_listrow(providers[i][0], providers[i][1],
                                        providers[i][2], providers[i][3])
                self.listbox.add(row)
                i += 1
        else:
            vbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

            logo_image = Gtk.Image()
            logo_image.set_from_icon_name("dialog-information-symbolic",
                                           Gtk.IconSize.DIALOG)
            vbox.pack_start(logo_image, False, False, 6)

            no_proivders_label = Gtk.Label()
            no_proivders_label.set_text("There's no providers at the moment")
            vbox.pack_start(no_proivders_label, False, False, 6)

            box_outer.pack_start(vbox, True, True, 0)
            self.get_children()[0].pack_start(box_outer, True, True, 0)

    def update_list(self, id, name, secret_code, image):
        row = self.generate_listrow(id, name, secret_code, image)
        self.listbox.add(row)
        self.listbox.show_all()


    def generate_listrow(self, id, name, secret_code, logo):
        row = Gtk.ListBoxRow()
        row.get_style_context().add_class("application-list-row")
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        pass_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        pass_box.set_visible(False)
        vbox.pack_start(hbox, True, True, 6)
        vbox.pack_start(pass_box, True, True, 6)

        # ID
        label_id = Gtk.Label()
        label_id.set_text(str(id))
        label_id.set_visible(False)
        label_id.set_no_show_all(True)
        vbox.pack_end(label_id, False, False, 0)

        # Checkbox
        checkbox = Gtk.CheckButton()
        checkbox.set_visible(False)
        checkbox.set_no_show_all(True)
        checkbox.connect("toggled", self.select_application)
        hbox.pack_start(checkbox, False, True, 6)
        self.checkboxes.append(checkbox)

        # Provider logo
        provider_logo = self.app.provider.get_provider_image(logo)
        hbox.pack_start(provider_logo, False, True, 6)

        # Provider name
        application_name = Gtk.Label(xalign=0)
        application_name.get_style_context().add_class("application-name")
        application_name.set_text(name)
        hbox.pack_start(application_name, True, True, 6)
        # Copy button
        copy_event = Gtk.EventBox()
        copy_button = Gtk.Image(xalign=0)
        copy_button.set_from_icon_name("edit-copy-symbolic",
                                       Gtk.IconSize.SMALL_TOOLBAR)
        copy_button.set_tooltip_text("Copy the generated code..")
        copy_event.connect("button-press-event", self.copy_code)
        copy_event.add(copy_button)
        hbox.pack_end(copy_event, False, True, 6)

        # Remove button
        remove_event = Gtk.EventBox()
        remove_button = Gtk.Image(xalign=0)
        remove_button.set_from_icon_name("list-remove-symbolic",
                                         Gtk.IconSize.SMALL_TOOLBAR)
        remove_button.set_tooltip_text("Remove the source..")
        remove_event.add(remove_button)
        remove_event.connect("button-press-event", self.remove_application)
        hbox.pack_end(remove_event, False, True, 6)

        code_label = Gtk.Label(xalign=0)
        code_label.get_style_context().add_class("application-secret-code")
        # TODO : show the real secret code
        code_label.set_text(secret_code)
        pass_box.set_no_show_all(True)

        pass_box.pack_start(code_label, False, True, 0)

        row.add(vbox)
        return row


    def copy_code(self, *args):
        selected_row = self.listbox.get_selected_row()
        label = selected_row.get_children()[0].get_children()[1].get_children()
        code = label[0].get_text()
        try:
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            clipboard.clear()
            clipboard.set_text(code, len(code))
        except Exception as e:
            logging.error(str(e))

    def refresh_window(self, *args):
        mainbox = self.get_children()[0]
        self.checkboxes = []
        count = self.app.provider.count_providers()
        for widget in mainbox:
            mainbox.remove(widget)
        self.genereate_searchbar()
        self.generate_applications_list()

        headerbar = self.get_children()[1]
        left_box = headerbar.get_children()[0]
        right_box = headerbar.get_children()[1]
        right_box.get_children()[0].set_visible(count > 0)
        if count == 0:
            self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        if count > 0 and self.listbox:
            if self.listbox.get_selection_mode() == Gtk.SelectionMode.MULTIPLE:
                left_box.get_children()[0].set_visible(count > 0)
        else:
            left_box.get_children()[0].set_visible(False)
        self.get_children()[0].show_all()

    # TODO : add remove from database
    def remove_application(self, *args):
        confirmation = ConfirmationMessage(self, "Are you sure??")
        confirmation.show()
        if confirmation.get_confirmation():
            if self.listbox.get_selected_row():
                selected_row = self.listbox.get_selected_row()
                del self.checkboxes[selected_row.get_index()]
                index = selected_row.get_index() + 1
                if index > len(self.listbox.get_children()) - 1:
                    index = selected_row.get_index() - 1
                self.listbox.select_row(self.listbox.get_row_at_index(index))
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
