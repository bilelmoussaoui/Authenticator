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
from .code import Code
from .database import Database
from .keyring import Keyring
from .logger import Logger


class Account(GObject.GObject, Thread):
    __gsignals__ = {
        'code_updated': (GObject.SignalFlags.RUN_LAST, None, (str,)),
        'counter_updated': (GObject.SignalFlags.RUN_LAST, None, (str,)),
        'removed': (GObject.SignalFlags.RUN_LAST, None, ()),
    }

    def __init__(self, _id, name, provider, secret_id):
        Thread.__init__(self)
        GObject.GObject.__init__(self)
        self.counter_max = 30
        self._alive = True
        self.counter = self.counter_max
        self.id = _id
        self.name = name
        self.provider = provider
        self.secret_id = secret_id
        _secret = Keyring.get_by_id(self.secret_id)
        if _secret:
            self._code = Code(_secret)
            self._code_generated = True
        else:
            self._code = None
            self._code_generated = False
            Logger.error("Could not read the secret code,"
                         "the keyring keys were reset manually")
        self.start()

    @staticmethod
    def create(name, provider, secret_id):
        encrypted_secret = sha256(secret_id.encode('utf-8')).hexdigest()
        obj = Database.get_default().insert(name, provider, encrypted_secret)

        Keyring.insert(encrypted_secret, provider, name, secret_id)
        return Account(obj['id'], name, provider, encrypted_secret)

    def update(self, **kwargs):
        self.name = kwargs.get("name", self.name)
        self.provider = kwargs.get("provider", self.provider)
        Database.get_default().update(kwargs, self.id)

    @property
    def secret_code(self):
        if self._code_generated:
            return self._code.secret_code
        return None

    def run(self):
        while self._code_generated and self._alive:
            self.counter -= 1
            if self.counter == 0:
                self.counter = self.counter_max
                self._code.update()
                self.emit("code_updated", self.secret_code)
            self.emit("counter_updated", self.counter)
            sleep(1)

    def kill(self):
        """
            Kill the row thread once it's removed
        """
        self._alive = False

    def remove(self):
        self.kill()
        Database.get_default().remove(self.id)
        Keyring.remove(self.secret_id)
        self.emit("removed")
        Logger.debug("Account '{}' with id {} was removed".format(self.name,
                                                                  self.id))

    def copy_token(self):
        """Copy the secret token to the clipboard."""
        Clipboard.set(self._code.secret_code)
