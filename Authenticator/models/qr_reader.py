"""
 Copyright © 2017 Bilal Elmoussaoui <bil.elmoussaoui@gmail.com>

 This file is part of Authenticator.

 Authenticator is free software: you can redistribute it and/or
 modify it under the terms of the GNU General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 Authenticator is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Authenticator. If not, see <http://www.gnu.org/licenses/>.
"""
import logging
from os import remove, path
from urllib.parse import urlparse, parse_qsl

from PIL import Image
from zbarlight import scan_codes

from .code import Code
from .logger import Logger


class QRReader:

    def __init__(self, filename):
        self.filename = filename
        self._codes = None

    def read(self):
        with open(self.filename, 'rb') as image_file:
            image = Image.open(image_file)
            image.load()
        self._codes = scan_codes('qrcode', image)
        self.remove()
        if self._codes:
            otpauth_url = self._codes[0].decode()
            self._codes = dict(parse_qsl(urlparse(otpauth_url)[4]))
            return self._codes.get("secret" )
        else:
            Logger.error("Invalid QR image")
            return None

    def remove(self):
        """
            remove image file for security reasons
        """
        if path.isfile(self.filename):
            remove(self.filename)
            Logger.debug("QR code image was removed for security reasons")

    def is_valid(self):
        """
            Validate if the QR code is a valid tfa
        """
        if isinstance(self._codes, dict):
            if set(["issuer", "secret"]).issubset(self._codes.keys()):
                return Code.is_valid(self._codes["secret"])
            else:
                return False
        else:
            return False
