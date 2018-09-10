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
                                            "id": Secret.SchemaAttributeType.STRING,
                                            "name": Secret.SchemaAttributeType.STRING,
                                        })

    @staticmethod
    def get_default():
        if Keyring.instance is None:
            Keyring.instance = Keyring()
        return Keyring.instance

    @staticmethod
    def get_by_id(secret_id):
        """
        Return the OTP token based on a secret ID.

        :param secret_id: the secret ID associated to an OTP token
        :type secret_id: str
        :return: the secret OTP token.
        """
        schema = Keyring.get_default().schema
        password = Secret.password_lookup_sync(
            schema, {"id": str(secret_id)}, None)
        return password

    @staticmethod
    def insert(secret_id, provider, username, token):
        """
        Save a secret OTP token.

        :param secret_id: The secret ID associated to the OTP token
        :param provider: the provider name
        :param username: the username
        :param token: the secret OTP token.


        """
        schema = Keyring.get_default().schema

        data = {
            "id": str(secret_id),
            "name": str(username),
        }
        Secret.password_store_sync(
            schema,
            data,
            Secret.COLLECTION_DEFAULT,
            "{provider} OTP ({username})".format(
                provider=provider, username=username),
            token,
            None
        )

    @staticmethod
    def remove(secret_id):
        """
        Remove a specific secret OTP token.

        :param secret_id: the secret ID associated to the OTP token
        :return bool: Either the token was removed successfully or not
        """
        schema = Keyring.get_default().schema
        success = Secret.password_clear_sync(
            schema, {"id": str(secret_id)}, None)
        return success
