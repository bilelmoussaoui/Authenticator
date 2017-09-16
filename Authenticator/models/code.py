"""
 Copyright © 2017 Bilal Elmoussaoui <bil.elmoussaoui@gmail.com>

 This file is part of Gnome Authenticator.

 Gnome Authenticator is free software: you can redistribute it and/or
 modify it under the terms of the GNU General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 TwoFactorAuth is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Gnome Authenticator. If not, see <http://www.gnu.org/licenses/>.
"""
import logging
import binascii
from base64 import b32decode
try:
    from pyotp import TOTP
except ImportError:
    logging.error("Impossible to import TOTP, please install PyOTP first")


class Code:
    password = None

    def __init__(self, secret_code):
        self.secret_code = secret_code
        self.create()

    @staticmethod
    def is_valid(code):
        """
            Check if the secret code is a valid one
        """
        try:
            b32decode(code, casefold=True)
            return True
        except (binascii.Error, ValueError):
            return False

    def create(self):
        """
            Create a tfa code
        """
        try:
            self.totp = TOTP(self.secret_code)
            self.password = self.totp.now()
        except Exception as e:
            logging.error("Couldn't generate two factor code : %s" % str(e))

    def update(self):
        """
            Update the code
        """
        self.password = self.totp.now()

    def get_secret_code(self):
        try:
            if self.password:
                return self.password
            else:
                raise AttributeError
        except AttributeError as e:
            logging.error("Couldn't generate the code : %s " % str(e))
            return None
