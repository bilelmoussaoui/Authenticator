"""
 Copyright © 2017 Bilal Elmoussaoui <bil.elmoussaoui@gmail.com>

 This file is part of Gnome Authenticator.

 Gnome Authenticator is free software: you can redistribute it and/or
 modify it under the terms of the GNU General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 TwoFactorAuth is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Gnome Authenticator. If not, see <http://www.gnu.org/licenses/>.
"""
import sqlite3
from hashlib import sha256
from os import path, makedirs

from gi.repository import GLib
from .logger import Logger


class Database:
    """SQL database handler."""

    # Default instance
    instance = None

    def __init__(self):
        database_file = path.join(GLib.get_user_config_dir(), 
                                  'Authenticator/database.db')
        makedirs(path.dirname(database_file), exist_ok=True)
        if not path.exists(database_file):
            with open(database_file, 'w') as file_obj:
                file_obj.write('')
        self.conn = sqlite3.connect(database_file)
        if not self.is_table_exists():
            Logger.debug("SQL: Table 'accounts' does not exists")
            self.create_table()
            Logger.debug("SQL: Table 'accounts' created successfully")

    @staticmethod
    def get_default():
        """Return the default instance of database"""
        if Database.instance is None:
            Database.instance = Database()
        return Database.instance

    def insert(self, name, secret_code, image):
        """
        Insert a new account to the database
        :param name: Account name
        :param secret_code: the secret code
        :param image: the image name/url
        :return: a dict with id, name, image & encrypted_secret
        """
        encrypted_secret = sha256(secret_code.encode('utf-8')).hexdigest()
        query = "INSERT INTO accounts (name, secret_code, image) VALUES (?, ?, ?)"
        try:
            self.conn.execute(query, [name, secret_code, image])
            self.conn.commit()
            return {
                "id": self.latest_id,
                "name": name,
                "encrypted_secret": encrypted_secret,
                "image": image
            }
        except Exception as error:
            Logger.error("[SQL] Couldn't add a new account")
            Logger.error(str(error))

    def get_secret_code(self, id_):
        """
        Get the secret code by id
        :param id_: int the account id
        :return: the secret id
        """
        query = "SELECT secret_code FROM accounts WHERE uid=?"
        try:
            data = self.conn.cursor().execute(query, (id_,))
            return data.fetchone()[0]
        except Exception as error:
            Logger.error("[SQL] Couldn't get account secret code")
            Logger.error(str(error))
        return None

    def remove(self, id_):
        """
            Remove an account by id
            :param id_: (int) account uid
        """
        query = "DELETE FROM accounts WHERE uid=?"
        try:
            self.conn.execute(query, (id_,))
            self.conn.commit()
        except Exception as error:
            Logger.error("[SQL] Couldn't remove account by uid")
            Logger.error(str(error))

    def update(self, id_, name, image):
        """
        Update an account by id
        :param id_: the account id
        :param name: the new account name
        :param image: the new account image
        """
        query = "UPDATE accounts SET name=?, image=? WHERE uid=?"
        try:
            self.conn.execute(query, (name, image, id_, ))
            self.conn.commit()
        except Exception as error:
            Logger.error("[SQL] Couldn't update account name by id")
            Logger.error(error)

    @property
    def count(self):
        """
            Count number of accounts
           :return: (int) count
        """
        query = "SELECT COUNT(uid) AS count FROM accounts"
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
            Fetch list of accounts
            :return: (tuple) list of accounts
        """
        query = "SELECT * FROM accounts"
        try:
            data = self.conn.cursor().execute(query)
            return data.fetchall()
        except Exception as error:
            Logger.error("[SQL] Couldn't fetch accounts list")
            Logger.error(str(error))
        return None

    @property
    def latest_id(self):
        """
            Get the latest uid on accounts table
            :return: (int) latest uid
        """
        query = "SELECT uid FROM accounts ORDER BY uid DESC LIMIT 1;"
        try:
            data = self.conn.cursor().execute(query)
            return data.fetchone()[0]
        except Exception as error:
            Logger.error("[SQL] Couldn't fetch the latest uid")
            Logger.error(str(error))
        return None

    def create_table(self):
        """Create 'accounts' table."""
        query = '''CREATE TABLE "accounts" (
            "uid" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE ,
            "name" VARCHAR NOT NULL ,
            "secret_code" VARCHAR NOT NULL ,
            "image" TEXT NOT NULL
        )'''
        try:
            self.conn.execute(query)
            self.conn.commit()
        except Exception as error:
            Logger.error("[SQL] Impossible to create table 'accounts'")
            Logger.error(str(error))

    def is_table_exists(self):
        """
            Check if accounts table exists
            :return: (bool)
        """
        query = "SELECT uid from accounts LIMIT 1"
        try:
            self.conn.cursor().execute(query)
            return True
        except Exception as e:
            return False
