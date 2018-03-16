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
from gi import require_version
require_version('Secret', '1')
from gi.repository import Secret


class Keyring:
    ID = "com.github.bilelmoussaoui.Authenticator"
    instance = None


    def __init__(self):
        self.schema = Secret.Schema.new(Keyring.ID, 
        Secret.SchemaFlags.NONE,
        {
            "id": Secret.SchemaAttributeType.STRING
        })

    @staticmethod
    def get_default():
        if Keyring.instance is None:
            Keyring.instance = Keyring()
        return Keyring.instance

    @staticmethod
    def get_by_id(id_):
        """Return the secret code"""
        schema = Keyring.get_default().schema
        password = Secret.password_lookup_sync(schema, { "id": id_ }, None)
        return password

    @staticmethod
    def insert(id_, secret_code):
        """
        Insert a secret code to Keyring database
        :param id_: the encrypted id
        :param secret_code: the secret code
        """
        schema = Keyring.get_default().schema
        Secret.password_store_sync(schema, {
            "id": id_,
        }, Secret.COLLECTION_DEFAULT, "", secret_code, None)

    @staticmethod
    def remove(id_):
        """
        Remove an account from Gnome Keyring by secret id
        :param id_: the encrypted secret code.
        :return: bool
        """
        schema = Keyring.get_default().schema
        removed = Secret.password_clear_sync(schema, { "id": id_ }, None)
        return removed