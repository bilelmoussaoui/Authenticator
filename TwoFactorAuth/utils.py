from os import path, mknod, makedirs, environ as env
from gi.repository import GdkPixbuf, Gtk
import logging
from subprocess import PIPE, Popen, call
from time import strftime

def is_gnome():
    return env.get("XDG_CURRENT_DESKTOP").lower() == "gnome"

def get_home_path():
    return path.expanduser("~")

def get_icon(image):
    """
        Generate a GdkPixbuf image
        :param image: icon name or image path
        :return: GdkPixbux Image
    """
    directory = path.join(env.get("DATA_DIR"), "applications") + "/"
    theme = Gtk.IconTheme.get_default()
    if path.isfile(directory + image) and path.exists(directory + image):
        icon = GdkPixbuf.Pixbuf.new_from_file(directory + image)
    elif path.isfile(image) and path.exists(image):
        icon = GdkPixbuf.Pixbuf.new_from_file(image)
    elif theme.has_icon(path.splitext(image)[0]):
        icon = theme.load_icon(path.splitext(image)[0], 48, 0)
    else:
        icon = theme.load_icon("image-missing", 48, 0)
    if icon.get_width() != 48 or icon.get_height() != 48:
        icon = icon.scale_simple(48, 48, GdkPixbuf.InterpType.BILINEAR)
    return icon

def create_file(file_path):
    if not (path.isfile(file_path) and path.exists(file_path)):
        dirs = file_path.split("/")
        i = 0
        while i < len(dirs) - 1:
            directory = "/".join(dirs[0:i + 1]).strip()
            if not path.exists(directory) and len(directory) != 0:
                makedirs(directory)
                logging.debug("Creating directory %s " % directory)
            i += 1
        mknod(file_path)
        return True
    else:
        return False

def screenshot_area(file_name):
    ink_flag = call(['which', 'gnome-screenshot'], stdout=PIPE, stderr=PIPE)
    if ink_flag == 0:
        p = Popen(["gnome-screenshot", "-a" , "-f", file_name],
                stdout=PIPE, stderr=PIPE)
        output, error = p.communicate()
        if error:
            error = error.decode("utf-8").split("\n")
            logging.debug("\n".join([e for e in error]))
        if not path.isfile(file_name):
            logging.debug("The screenshot was not token")
            return False
        return True
    else:
        logging.error("Couldn't find gnome-screenshot, please install it first")
        return False

def current_date_time():
    return strftime("%d_%m_%Y-%H:%M:%S")
