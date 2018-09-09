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
from threading import Thread
from time import sleep

from gi.repository import GObject

from .clipboard import Clipboard
from .database import Database
from .keyring import Keyring
from .logger import Logger
from .otp import OTP


class Account(GObject.GObject, Thread):
    __gsignals__ = {
        'otp_updated': (GObject.SignalFlags.RUN_LAST, None, (str,)),
        'counter_updated': (GObject.SignalFlags.RUN_LAST, None, (str,)),
        'removed': (GObject.SignalFlags.RUN_LAST, None, ()),
    }

    def __init__(self, _id, username, provider, secret_id):
        Thread.__init__(self)
        GObject.GObject.__init__(self)
        self.counter_max = 30
        self._alive = True
        self.counter = self.counter_max
        self.id = _id
        self.username = username
        self.provider = provider
        self.secret_id = secret_id
        token = Keyring.get_by_id(self.secret_id)
        if token:
            self.otp = OTP(token)
            self._code_generated = True
        else:
            self.otp = None
            self._code_generated = False
            Logger.error("Could not read the secret code,"
                         "the keyring keys were reset manually")
        self.start()

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

    def update(self, username, provider):
        """
        Update the account name and/or provider.
        :param username: the account's username
        :param provider: the account's provider
        """
        Database.get_default().update(username, provider, self.id)

    def run(self):
        while self._code_generated and self._alive:
            self.counter -= 1
            if self.counter == 0:
                self.counter = self.counter_max
                self.otp.update()
                self.emit("otp_updated", self.otp.pin)
            self.emit("counter_updated", self.counter)
            sleep(1)

    def kill(self):
        """
            Kill the row thread once it's removed
        """
        self._alive = False

    def remove(self):
        """
        Remove the account.
        """
        self.kill()
        Database.get_default().remove(self.id)
        Keyring.remove(self.secret_id)
        self.emit("removed")
        Logger.debug("Account '{}' with id {} was removed".format(self.name,
                                                                  self.id))

    def copy_pin(self):
        """Copy the OTP to the clipboard."""
        Clipboard.set(self.otp.pin)
