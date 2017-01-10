from TwoFactorAuth.models.settings import SettingsReader
from TwoFactorAuth.models.code import Code
from TwoFactorAuth.models.database import Database
import logging
from gi.repository import GObject
from threading import Thread
from time import sleep
from TwoFactorAuth.models.observer import Observer
from TwoFactorAuth.interfaces.account_observrable import AccountObservable, AccountRowObservable

class Account(GObject.GObject, Thread, Observer):
    __gsignals__ = {
        'code_updated': (GObject.SignalFlags.RUN_LAST, None, (bool,)),
        'name_updated': (GObject.SignalFlags.RUN_LAST, None, (bool,)),
        'counter_updated': (GObject.SignalFlags.RUN_LAST, None, (bool,)),
        'removed': (GObject.SignalFlags.RUN_LAST, None, (bool,)),
    }
    counter_max = 30
    counter = 30
    alive = True
    code_generated = True


    def __init__(self, app, db):
        Thread.__init__(self)
        GObject.GObject.__init__(self)
        self.db = db
        cfg = SettingsReader()
        self.counter_max = cfg.read("refresh-time", "preferences")
        self.counter = self.counter_max
        self.account_id = app[0]
        self.account_name = app[1]
        self.secret_code = Database.fetch_secret_code(app[2])
        if self.secret_code:
            self.code = Code(self.secret_code)
        else:
            self.code_generated = False
            logging.error("Could not read the secret code,"
                          "the keyring keys were reset manually")
        self.logo = app[3]
        self.account_observerable = AccountObservable()
        self.row_observerable = AccountRowObservable()
        self.start()

    def do_name_updated(self, *args):
        self.account_observerable.update_observers(name=self.get_name())

    def do_counter_updated(self, *args):
        self.account_observerable.update_observers(counter=self.get_counter())

    def do_code_updated(self, *args):
        self.account_observerable.update_observers(code=self.get_code())

    def do_removed(self, *args):
        self.row_observerable.update_observers(removed=self.get_id())

    def update(self, alive):
        if not alive:
            self.kill()

    def run(self):
        while self.code_generated and self.alive:
            self.counter -= 1
            if self.counter == 0:
                self.counter = self.counter_max
                self.code.update()
                self.emit("code_updated", True)
            self.emit("counter_updated", True)
            sleep(1)

    def get_id(self):
        """
            Get the application id
            :return: (int): row id
        """
        return self.account_id

    def get_name(self):
        """
            Get the application name
            :return: (str): application name
        """
        return self.account_name

    def get_logo(self):
        return self.logo

    def get_code(self):
        return self.code.get_secret_code()

    def get_counter(self):
        return self.counter

    def get_counter_max(self):
        return self.counter_max

    def kill(self):
        """
            Kill the row thread once it's removed
        """
        self.alive = False

    def remove(self):
        self.db.remove_by_id(self.get_id())
        self.emit("removed", True)

    def set_name(self, name):
        self.db.update_name_by_id(self.get_id(), name)
        self.account_name = name
        self.emit("name_updated", True)
