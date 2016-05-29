import sqlite3
import logging
from os import path, mknod, makedirs
from gi.repository import GdkPixbuf, Gtk

class Authenticator:

    def __init__(self):
        home = path.expanduser("~")
        database_file = home + '/.config/TwoFactorAuth/database.db'
        if not (path.isfile(database_file) and path.exists(database_file)):
            dirs = database_file.split("/")
            i = 0
            while i < len(dirs) -1:
                directory = "/".join(dirs[0:i+1]).strip()
                if not path.exists(directory) and len(directory) != 0:
                    makedirs(directory)
                    logging.debug("Creating directory %s " %directory)
                i += 1
            mknod(database_file)
            logging.debug("Creating database file %s " % database_file)
        self.conn = sqlite3.connect(database_file)
        if not self.is_table_exists():
            logging.debug("Table 'applciations' does not exists, creating it now...")
            self.create_table()
            logging.debug("Table 'applications' created successfully")


    def add_application(self, name, secret_code, image):
        t = (name, secret_code, image,)
        query = "INSERT INTO applications (name, secret_code, image) VALUES (?, ?, ?)"
        try:
            self.conn.execute(query, t)
            self.conn.commit()
        except Exception as e:
            logging.error("Couldn't add a new application : %s ", str(e))

    def remove_by_id(self, id):
        query = "DELETE FROM applications WHERE id=?"
        try:
            self.conn.execute(query, (id,))
            self.conn.commit()
        except Exception as e:
            logging.error("Couldn't remove application by id : %s with error : %s" % (id,str(e)))

    def count(self):
        c = self.conn.cursor()
        query = "SELECT COUNT(id) AS count FROM applications"
        try:
            data = c.execute(query)
            return data.fetchone()[0]
        except Exception as e:
            logging.error("Couldn't count applications list : %s " % str(e))
            return None

    def fetch_apps(self):
        c = self.conn.cursor()
        query = "SELECT * FROM applications"
        try:
            data = c.execute(query)
            return data.fetchall()
        except Exception as e:
            logging.error(query)
            logging.error("Couldn't fetch applications list")
            logging.error(str(e))
            return None

    @staticmethod
    def get_auth_icon(image, pkgdatadir):
        directory = pkgdatadir + "/data/logos/"
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
        c = self.conn.cursor()
        query = "SELECT id FROM applications ORDER BY id DESC LIMIT 1;"
        try:
            data = c.execute(query)
            return data.fetchone()[0]
        except Exception as e:
            logging.error("Couldn't fetch the latest id %s" % str(e))
            return None

    def create_table(self):
        query = '''CREATE TABLE "applications" (
            "id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE ,
            "name" VARCHAR NOT NULL ,
            "secret_code" VARCHAR NOT NULL  UNIQUE ,
            "image" TEXT NOT NULL
        )'''
        try:
            self.conn.execute(query)
            self.conn.commit()
        except Exception as e:
            logging.error("SQL : imossibile to create table 'applications' %s " % str(err))

    def is_table_exists(self):
        query = "SELECT id from applications LIMIT 1"
        c = self.conn.cursor()
        try:
            data = c.execute(query)
            return True
        except Exception as e:
            return False
