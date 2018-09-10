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
from threading import Thread
from time import sleep

from gi.repository import GObject


class AccountsManager(GObject.GObject, Thread):
    __gsignals__ = {
        'counter_updated': (GObject.SignalFlags.RUN_LAST, None, (str,)),
    }
    instance = None

    def __init__(self):
        GObject.GObject.__init__(self)
        Thread.__init__(self)
        self._accounts = []
        self._alive = True

        self.counter_max = 30
        self.counter = self.counter_max
        self.start()

    @staticmethod
    def get_default():
        if AccountsManager.instance is None:
            AccountsManager.instance = AccountsManager()
        return AccountsManager.instance

    def add(self, account):
        self._accounts.append(account)

    def kill(self):
        self._alive = False

    def update_childes(self, signal, data=None):
        for child in self._accounts:
            if data:
                child.emit(signal, data)
            else:
                child.emit(signal)

    def run(self):
        while self._alive:
            self.counter -= 1
            if self.counter == 0:
                self.counter = self.counter_max
                self.update_childes("otp_out_of_date")
            self.emit("counter_updated", self.counter)
            sleep(1)
