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
from pyzbar.pyzbar import decode

from .code import Code
from .logger import Logger


class QRReader:

    def __init__(self, filename):
        self.filename = filename
        self._codes = None

    def read(self):
        decoded_data = decode(Image.open(self.filename))
        if path.isfile(self.filename):
            remove(self.filename)
        try:
            url = urlparse(decoded_data[0].data.decode())
            query_params = parse_qsl(url.query)
            self._codes =  dict(query_params)
            return self._codes.get("secret")
        except KeyError:
            Logger.error("Invalid QR image")
            return None

    def is_valid(self):
        """
            Validate if the QR code is a valid tfa
        """
        if isinstance(self._codes, dict):
            return Code.is_valid(self._codes.get("secret"))
        return False
