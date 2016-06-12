import sqlite3
import logging
from os import path, mknod, makedirs, environ as env
from gi.repository import GdkPixbuf, Gtk
from gi.repository import GnomeKeyring as GK
from hashlib import sha256

class Authenticator:

    def __init__(self):
        home = path.expanduser("~")
        database_file = home + '/.config/TwoFactorAuth/database.db'
        # Create missing folders
        if not (path.isfile(database_file) and path.exists(database_file)):
            dirs = database_file.split("/")
            i = 0
            while i < len(dirs) - 1:
                directory = "/".join(dirs[0:i + 1]).strip()
                if not path.exists(directory) and len(directory) != 0:
                    makedirs(directory)
                    logging.debug("Creating directory %s " % directory)
                i += 1
            # create database file
            mknod(database_file)
            logging.debug("Creating database file %s " % database_file)
        # Connect to database
        self.conn = sqlite3.connect(database_file)
        if not self.is_table_exists():
            logging.debug(
                "SQL: Table 'accounts' does not exists, creating it now...")
            self.create_table()
            logging.debug("SQL: Table 'accounts' created successfully")

    @staticmethod
    def fetch_secret_code(secret_code):
        attr = GK.Attribute.list_new()
        GK.Attribute.list_append_string(attr, 'id', secret_code)
        result, value = GK.find_items_sync(GK.ItemType.GENERIC_SECRET, attr)
        if result == GK.Result.OK:
            return value[0].secret
        else:
            return None

    def add_account(self, name, secret_code, image):
        """
            Add an account to accounts table
            :param name: (str) account name
            :param secret_code: (str) ASCII Secret code
            :param image: image path or icon name
            :return:
        """
        encrypted_secret = sha256(secret_code.encode('utf-8')).hexdigest()
        t = (name, encrypted_secret, image,)
        query = "INSERT INTO accounts (name, secret_code, image) VALUES (?, ?, ?)"
        try:
            GK.create_sync("TwoFactorAuth", None)
            attr = GK.Attribute.list_new()
            GK.Attribute.list_append_string(attr, 'id', encrypted_secret)
            GK.Attribute.list_append_string(attr, 'secret_code', secret_code)
            GK.item_create_sync("TwoFactorAuth", GK.ItemType.GENERIC_SECRET, repr(encrypted_secret), attr,
                                secret_code, False)
            self.conn.execute(query, t)
            self.conn.commit()
        except Exception as e:
            logging.error("SQL: Couldn't add a new account : %s ", str(e))

    def get_secret_code(self, uid):
        """
            Count number of accounts
           :return: (int) count
        """
        c = self.conn.cursor()
        query = "SELECT secret_code FROM accounts WHERE uid=?"
        try:
            data = c.execute(query, (uid,))
            return data.fetchone()[0]
        except Exception as e:
            logging.error(
                "SQL: Couldn't get account secret code : %s " % str(e))
            return None

    def remove_by_id(self, uid):
        """
            Remove an account by uid
            :param uid: (int) account uid
            :return:
        """
        secret_code = self.get_secret_code(uid)
        if secret_code:
            found = False
            (result, ids) = GK.list_item_ids_sync("TwoFactorAuth")
            for gid in ids:
                (result, item) = GK.item_get_info_sync("TwoFactorAuth", gid)
                if result == GK.Result.OK:
                    if item.get_display_name().strip("'") == secret_code:
                        found = True
                        break
            if found:
                GK.item_delete_sync("TwoFactorAuth", gid)
        query = "DELETE FROM accounts WHERE uid=?"
        try:
            self.conn.execute(query, (uid,))
            self.conn.commit()
        except Exception as e:
            logging.error(
                "SQL: Couldn't remove account by uid : %s with error : %s" % (uid, str(e)))

    def count(self):
        """
            Count number of accounts
           :return: (int) count
        """
        c = self.conn.cursor()
        query = "SELECT COUNT(uid) AS count FROM accounts"
        try:
            data = c.execute(query)
            return data.fetchone()[0]
        except Exception as e:
            logging.error(
                "SQL: Couldn't count accounts list : %s " % str(e))
            return None

    def fetch_apps(self):
        """
            Fetch list of accounts
            :return: (tuple) list of accounts
        """
        c = self.conn.cursor()
        query = "SELECT * FROM accounts"
        try:
            data = c.execute(query)
            return data.fetchall()
        except Exception as e:
            logging.error("SQL: Couldn't fetch accounts list  %s" % str(e))
            return None

    @staticmethod
    def get_auth_icon(image):
        """
            Generate a GdkPixbuf image
            :param image: icon name or image path
            :return: GdkPixbux Image
        """
        directory = path.join(env.get("DATA_DIR"), "applications") + "/"
        theme = Gtk.IconTheme.get_default()
        if path.isfile(directory + image) and path.exists(directory + image):
            icon = GdkPixbuf.Pixbuf.new_from_file(directory + image)
        elif path.isfile(image) and path.exists(image):
            icon = GdkPixbuf.Pixbuf.new_from_file(image)
        elif theme.has_icon(path.splitext(image)[0]):
            icon = theme.load_icon(path.splitext(image)[0], 48, 0)
        else:
            icon = theme.load_icon("image-missing", 48, 0)
        if icon.get_width() != 48 or icon.get_height() != 48:
            icon = icon.scale_simple(48, 48,
                                     GdkPixbuf.InterpType.BILINEAR)
        return icon

    def get_latest_id(self):
        """
            Get the latest uid on accounts table
            :return: (int) latest uid
        """
        c = self.conn.cursor()
        query = "SELECT uid FROM accounts ORDER BY uid DESC LIMIT 1;"
        try:
            data = c.execute(query)
            return data.fetchone()[0]
        except Exception as e:
            logging.error("SQL: Couldn't fetch the latest uid %s" % str(e))
            return None

    def create_table(self):
        """
            Create accounts table
        """
        query = '''CREATE TABLE "accounts" (
            "uid" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE ,
            "name" VARCHAR NOT NULL ,
            "secret_code" VARCHAR NOT NULL ,
            "image" TEXT NOT NULL
        )'''
        try:
            self.conn.execute(query)
            self.conn.commit()
        except Exception as e:
            logging.error(
                "SQL: impossible to create table 'accounts' %s " % str(e))

    def is_table_exists(self):
        """
            Check if accounts table exists
            :return: (bool)
        """
        query = "SELECT uid from accounts LIMIT 1"
        c = self.conn.cursor()
        try:
            data = c.execute(query)
            return True
        except Exception as e:
            return False
