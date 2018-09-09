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
import binascii

from .logger import Logger

try:
    from pyotp import TOTP
except ImportError:
    Logger.error("Impossible to import TOTP, please install PyOTP first")


class OTP(TOTP):
    """
        OTP (One-time password) handler using PyOTP.
    """

    def __init__(self, token):
        """
        :param token: the OTP token.
        """
        TOTP.__init__(self, token)
        self.pin = None
        self.update()

    @staticmethod
    def is_valid(token):
        """
        Validate a OTP token.

        :param token: OTP token
        :type token: str

        :return: bool
        """
        try:
            TOTP(token).now()
            return True
        except (binascii.Error, ValueError, TypeError):
            return False

    def update(self):
        """
            Generate a new OTP based on the same token.
        """
        try:
            self.pin = self.now()
        except binascii.Error:
            self.pin = None
