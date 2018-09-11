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
import json

from .account import Account
from .accounts_manager import AccountsManager
from .keyring import Keyring


class Backup:

    def __init__(self):
        pass

    @staticmethod
    def import_accounts(accounts):
        from ..widgets.accounts import AccountsWidget
        accounts_widget = AccountsWidget.get_default()
        accounts_manager = AccountsManager.get_default()
        for account in accounts:
            try:
                new_account = Account.create_from_json(account)
                accounts_widget.append(new_account)
                accounts_manager.add(new_account)
            except Exception:
                pass

    @staticmethod
    def export_accounts():
        accounts = AccountsManager.get_default().accounts
        exported_accounts = []
        for account in accounts:
            json_account = account.to_json()
            if json_account:
                exported_accounts.append(json_account)
        return exported_accounts


class BackupJSON:

    def __init__(self):
        pass

    @staticmethod
    def export_file(filename):
        accounts = Backup.export_accounts()
        with open(filename, 'w') as outfile:
            json.dump(accounts, outfile, sort_keys=True, indent=4)

    @staticmethod
    def import_file(filename):
        with open(filename, 'r') as infile:
            accounts = json.load(infile)
        Backup.import_accounts(accounts)


class BackupPGPJSON:
    def __init__(self):
        pass

    @staticmethod
    def export_file(filename, fingerprint):
        from .gnupg import GPG
        accounts = Backup.export_accounts()
        data = json.dumps(accounts, sort_keys=True, indent=4)
        encrypted_data = GPG.get_default().encrypt(data, fingerprint)
        with open(filename, 'w') as outfile:
            outfile.write(str(encrypted_data))
