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
from hashlib import sha256

from gi.repository import GObject

from .clipboard import Clipboard
from .database import Database
from .keyring import Keyring
from .logger import Logger
from .otp import OTP


class Account(GObject.GObject):
    __gsignals__ = {
        'otp_out_of_date': (GObject.SignalFlags.RUN_LAST, None, ()),
        'otp_updated': (GObject.SignalFlags.RUN_LAST, None, (str,)),
        'removed': (GObject.SignalFlags.RUN_LAST, None, ()),
    }

    def __init__(self, _id, username, provider, secret_id):
        GObject.GObject.__init__(self)
        self.id = _id
        self.username = username
        self.provider = provider
        self.secret_id = secret_id
        token = Keyring.get_by_id(self.secret_id)
        self.connect("otp_out_of_date", self._on_otp_out_of_date)
        if token:
            self.otp = OTP(token)
            self._code_generated = True
        else:
            self.otp = None
            self._code_generated = False
            Logger.error("Could not read the secret code,"
                         "the keyring keys were reset manually")

    @staticmethod
    def create(username, provider, token):
        """
        Create a new Account.
        :param username: the account's username
        :param provider: the account's provider
        :param token: the OTP secret token
        :return: Account object
        """
        # Encrypt the token to create a secret_id
        secret_id = sha256(token.encode('utf-8')).hexdigest()
        # Save the account
        obj = Database.get_default().insert(username, provider, secret_id)
        Keyring.insert(secret_id, provider, username, token)

        return Account(obj['id'], username, provider, secret_id)

    @staticmethod
    def get_by_id(id_):
        obj = Database.get_default().get_by_id(id_)
        return Account(obj['id'], obj['username'], obj['provider'], obj['secret_id'])

    def update(self, username, provider):
        """
        Update the account name and/or provider.
        :param username: the account's username
        :param provider: the account's provider
        """
        Database.get_default().update(username, provider, self.id)

    def remove(self):
        """
        Remove the account.
        """
        Database.get_default().remove(self.id)
        Keyring.remove(self.secret_id)
        self.emit("removed")
        Logger.debug("Account '{}' with id {} was removed".format(self.username,
                                                                  self.id))

    def copy_pin(self):
        """Copy the OTP to the clipboard."""
        Clipboard.set(self.otp.pin)

    def _on_otp_out_of_date(self, *_):
        if self._code_generated:
            self.otp.update()
            self.emit("otp_updated", self.otp.pin)
