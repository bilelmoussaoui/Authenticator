#!/usr/bin/env python3
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
from os import path, mknod, makedirs, environ as env
from gi.repository import GdkPixbuf, Gtk, Gio, GLib
import logging
from subprocess import PIPE, Popen, call
from tempfile import NamedTemporaryFile


def is_gnome():
    """
        Check if the current distro is gnome
    """
    return env.get("XDG_CURRENT_DESKTOP").lower() == "gnome"


def show_app_menu():
    try:
        source = Gio.SettingsSchemaSource.get_default()
        path = "org.gnome.desktop.wm.preferences"
        key = "button-layout"
        source.lookup(path, True)
        gsettings = Gio.Settings.new(path)
        value = gsettings.get_value(key)
        value = str(value).strip("'")
        #  "appmenu" in value or
        return not is_gnome()
    except Exception as e:
        logging.critical("Couldn't load gsettings source %s " % str(e))


def get_icon(image, size):
    """
        Generate a GdkPixbuf image
        :param image: icon name or image path
        :return: GdkPixbux Image
    """
    directory = path.join(env.get("DATA_DIR"), "applications", "images") + "/"
    theme = Gtk.IconTheme.get_default()
    if theme.has_icon(path.splitext(image)[0]):
        icon = theme.load_icon(path.splitext(image)[0], size, 0)
    elif path.exists(directory + image):
        icon = GdkPixbuf.Pixbuf.new_from_file(directory + image)
    elif path.exists(image):
        icon = GdkPixbuf.Pixbuf.new_from_file(image)
    else:
        icon = theme.load_icon("image-missing", size, 0)
    if icon.get_width() != size or icon.get_height() != size:
        icon = icon.scale_simple(size, size, GdkPixbuf.InterpType.BILINEAR)
    return icon


def create_file(file_path):
    """
        Create a file and create parent folder if missing
    """
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


def screenshot_area():
    """
        Screenshot an area of the screen using gnome-screenshot
        used to QR scan
    """
    ink_flag = call(['which', 'gnome-screenshot'], stdout=PIPE, stderr=PIPE)
    if ink_flag == 0:
        file_name = path.join(GLib.get_tmp_dir(), NamedTemporaryFile().name)
        p = Popen(["gnome-screenshot", "-a", "-f", file_name],
                  stdout=PIPE, stderr=PIPE)
        output, error = p.communicate()
        if error:
            error = error.decode("utf-8").split("\n")
            logging.error("\n".join([e for e in error]))
        if not path.isfile(file_name):
            logging.debug("The screenshot was not token")
            return False
        return file_name
    else:
        logging.error(
            "Couldn't find gnome-screenshot, please install it first")
        return False

