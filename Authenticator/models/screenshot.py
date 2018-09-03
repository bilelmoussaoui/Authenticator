from os import path
from tempfile import NamedTemporaryFile
from gi.repository import Gio, GLib


class GNOMEScreenshot:

    interface = "org.gnome.Shell.Screenshot"

    @staticmethod
    def area(filename=None):
        if not filename:
            filename = path.join(GLib.get_user_cache_dir(),
                                path.basename(NamedTemporaryFile().name))
        bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        screen_proxy = Gio.DBusProxy.new_sync(bus,
                                              Gio.DBusProxyFlags.NONE,
                                              None,
                                              "org.gnome.Shell.Screenshot",
                                              "/org/gnome/Shell/Screenshot",
                                              "org.gnome.Shell.Screenshot",
                                              None)
        area = screen_proxy.call_sync('SelectArea', None, Gio.DBusCallFlags.NONE,
                                      -1, None).unpack()

        args = GLib.Variant('(iiiibs)', (
            area[0],
            area[1],
            area[2],
            area[3],
            False, filename
        )
        )
        screenshot = screen_proxy.call_sync('ScreenshotArea', args,
                                            Gio.DBusCallFlags.NONE, -1, None)
        results = screenshot.unpack()
        if results[0]:
            return results[1]
        return None
