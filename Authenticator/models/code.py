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

    def __init__(self, token):
        self._token = token
        self._secret_code = None
        self.create()

    @staticmethod
    def is_valid(token):
        """Validate a token."""
        try:
            b32decode(token, casefold=True)
            return True
        except (binascii.Error, ValueError):
            return False

    def create(self):
        """
            Create a tfa code
        """
        try:
            self._totp = TOTP(self._token)
            self._secret_code = self._totp.now()
        except Exception as e:
            logging.error("Couldn't generate two factor code : %s" % str(e))

    def update(self):
        """
            Update the code
        """
        self._secret_code = self._totp.now()

    @property
    def secret_code(self):
        if self._secret_code:
            return self._secret_code
        return None