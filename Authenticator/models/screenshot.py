import dbus
from os import path
from tempfile import NamedTemporaryFile, gettempdir


class GNOMEScreenshot:

    interface = "org.gnome.Shell.Screenshot"

    @staticmethod
    def area(filename=None):
        if not filename:
            filename = path.join(gettempdir(), NamedTemporaryFile().name)
        bus = dbus.SessionBus()
        shell_obj = bus.get_object(GNOMEScreenshot.interface,
                                   "/org/gnome/Shell/Screenshot")
        screen_intf = dbus.Interface(shell_obj, GNOMEScreenshot.interface)

        area = screen_intf.SelectArea()
        x = dbus.Int64(area[0])
        y = dbus.Int64(area[1])
        width = dbus.Int64(area[2])
        height = dbus.Int64(area[3])

        screenshot = screen_intf.ScreenshotArea(x, y, width, height,
                                                False, filename)
        success = dbus.Boolean(screenshot[0])
        if success:
            filename = dbus.String(screenshot[1])
            return filename
        return None
