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
from os import path, environ
import logging
from subprocess import PIPE, Popen, call
from tempfile import NamedTemporaryFile, gettempdir


def is_gnome():
    """
        Check if the current distro is gnome
    """
    return environ.get("XDG_CURRENT_DESKTOP").lower() == "gnome"


def screenshot_area():
    """
        Screenshot an area of the screen using gnome-screenshot
        used to QR scan
    """
    ink_flag = call(['which', 'gnome-screenshot'], stdout=PIPE, stderr=PIPE)
    if ink_flag == 0:
        file_name = path.join(gettempdir(), NamedTemporaryFile().name)
        _, error = Popen(["gnome-screenshot", "-a", "-f", file_name],
                         stdout=PIPE, stderr=PIPE).communicate()
        if error:
            error = error.decode("utf-8").split("\n")
            logging.error("\n".join([e for e in error]))
        if not path.isfile(file_name):
            logging.debug("The screenshot was not token")
            return None
        return file_name
    else:
        logging.error("Couldn't find gnome-screenshot"
                      ", please install it first")
    return None
