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

 You  ould have received a copy of the GNU General Public License
 along with Authenticator. If not, see <http://www.gnu.org/licenses/>.
"""
import sqlite3
from collections import OrderedDict
from os import path, makedirs

from gi.repository import GLib

from .logger import Logger


class Database:
    """SQL database handler."""

    # Default instance
    instance = None
    # Database version number
    db_version = 3

    table_name = "accounts"
    primary_key = "id"

    def __init__(self):
        self.__create_database_file()
        self.conn = sqlite3.connect(self.db_file)
        if not self.__is_table_exists():
            Logger.debug("[SQL]: Table 'accounts' does not exist")
            self.__create_table()
            Logger.debug("[SQL]: Table 'accounts' created successfully")

    @staticmethod
    def get_default():
        """Return the default instance of database"""
        if Database.instance is None:
            Database.instance = Database()
        return Database.instance

    @property
    def db_file(self):
        return path.join(GLib.get_user_config_dir(),
                         'Authenticator',
                         'database-{}.db'.format(str(Database.db_version))
                         )

    def insert(self, username, provider, secret_id):
        """
        Insert a new account to the database
        :param username: Account name
        :param provider: Service provider
        :param secret_id: the secret code
        """
        query = "INSERT INTO {table} (username, provider, secret_id) VALUES (?, ?, ?)".format(
            table=self.table_name)
        try:
            self.conn.execute(query, [username, provider, secret_id])
            self.conn.commit()
            return OrderedDict([
                ("id", self.latest_id),
                ("name", username),
                ("provider", provider),
                ("secret_id", secret_id)
            ])
        except Exception as error:
            Logger.error("[SQL] Couldn't add a new account")
            Logger.error(str(error))

    def get_by_id(self, id_):
        """
            Get an account by the ID
            :param id_: int the account id
            :return: list: The account data
        """
        query = "SELECT * FROM {table} WHERE {key}=?".format(
            key=self.primary_key, table=self.table_name)
        try:
            data = self.conn.cursor().execute(query, (id_,))
            obj = data.fetchone()
            return OrderedDict([
                ("id", obj[0]),
                ("username", obj[1]),
                ("provider", obj[2]),
                ("secret_id", obj[3])
            ])
        except Exception as error:
            Logger.error("[SQL] Couldn't get account with ID={}".format(id_))
            Logger.error(str(error))
        return None

    def get_secret_id(self, id_):
        """
        Get the secret code by id
        :param id_: int the account id
        :return: the secret id
        """
        query = "SELECT secret_id FROM {table} WHERE {key}=?".format(
            key=self.primary_key, table=self.table_name)
        try:
            data = self.conn.cursor().execute(query, (id_,))
            return data.fetchone()[0]
        except Exception as error:
            Logger.error("[SQL] Couldn't get account secret code")
            Logger.error(str(error))
        return None

    def remove(self, id_):
        """
            Remove an account by ID.

            :param id_: the account ID
            :type id_: int
        """
        query = "DELETE FROM {table} WHERE {key}=?".format(
            key=self.primary_key, table=self.table_name)
        try:
            self.conn.execute(query, (id_,))
            self.conn.commit()
        except Exception as error:
            Logger.error("[SQL] Couldn't remove the account '{}'".format(id_))
            Logger.error(str(error))

    def clear(self):
        """
            Remove all the existing accounts.
        """
        query = "DELETE FROM {table}".format(table=self.table_name)
        self.conn.execute(query)
        self.conn.commit()

    def update(self, username, provider, id_):
        """
        Update an account by id
        """
        query = "UPDATE {table} SET username=?, provider=? WHERE {key}=?".format(key=self.primary_key,
                                                                                 table=self.table_name)
        try:
            self.conn.execute(query, (username, provider, id_))
            self.conn.commit()
        except Exception as error:
            Logger.error("[SQL] Couldn't update account name by id")
            Logger.error(error)

    def search(self, terms):
        filters = " ".join(terms)
        if filters:
            filters = "%" + filters + "%"
        query = "SELECT {key} FROM {table} WHERE username LIKE ?".format(table=self.table_name, key=self.primary_key)
        try:
            data = self.conn.cursor().execute(query, (filters,))
            return [str(account[0]) for account in data.fetchall()]
        except Exception as error:
            Logger.error("[SQL]: Couldn't search for an account")
            Logger.error(str(error))
            return []

    @property
    def count(self):
        """
            Count the total number of existing accounts.

           :return: int
        """
        query = "SELECT COUNT({key}) AS count FROM {table}".format(
            key=self.primary_key, table=self.table_name)
        try:
            data = self.conn.cursor().execute(query)
            return data.fetchone()[0]
        except Exception as error:
            Logger.error("[SQL]: Couldn't count accounts list")
            Logger.error(str(error))
        return None

    @property
    def accounts(self):
        """
            Retrieve the list of accounts.

            :return list
        """
        query = "SELECT * FROM {table} ORDER BY provider ASC, username DESC".format(
            table=self.table_name)
        try:
            data = self.conn.cursor().execute(query)
            accounts = data.fetchall()
            return [OrderedDict([
                ("id", account[0]),
                ("username", account[1]),
                ("provider", account[2]),
                ("secret_id", account[3])
            ]) for account in accounts]
        except Exception as error:
            Logger.error("[SQL] Couldn't fetch accounts list")
            Logger.error(str(error))
        return None

    @property
    def latest_id(self):
        """
            Retrieve the latest added ID from accounts.

            :return: int
        """
        query = "SELECT {key} FROM {table} ORDER BY {key} DESC LIMIT 1;".format(key=self.primary_key,
                                                                                table=self.table_name)
        try:
            data = self.conn.cursor().execute(query)
            return data.fetchone()[0]
        except Exception as error:
            Logger.error("[SQL] Couldn't fetch the latest id")
            Logger.error(str(error))
        return None

    def __create_database_file(self):
        """
        Create an empty database file for the first start of the application.
        """
        makedirs(path.dirname(self.db_file), exist_ok=True)
        if not path.exists(self.db_file):
            with open(self.db_file, 'w') as file_obj:
                file_obj.write('')

    def __create_table(self):
        """
        Create the needed tables to run the application.
        """
        query = '''CREATE TABLE "{table}" (
            "{key}" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
            "username" VARCHAR NOT NULL,
            "provider" VARCHAR NOT NULL,
            "secret_id" VARCHAR NOT NULL UNIQUE
        )'''.format(table=self.table_name, key=self.primary_key)
        try:
            self.conn.execute(query)
            self.conn.commit()
        except Exception as error:
            Logger.error("[SQL] Impossible to create table 'accounts'")
            Logger.error(str(error))

    def __is_table_exists(self):
        """
            Check if the used table are created or not.
            :return bool
        """
        query = "SELECT {key} from {table} LIMIT 1".format(
            key=self.primary_key, table=self.table_name)
        try:
            self.conn.cursor().execute(query)
            return True
        except Exception as e:
            return False
