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
from gi import require_version
require_version("GnomeKeyring", "1.0")
from gi.repository import GnomeKeyring as GK


class Keyring:
    ID = "org.gnome.Authenticator"

    @staticmethod
    def unlock():
        result = GK.unlock_sync(Keyring.ID, None)
        return result != GK.Result.CANCELLED

    @staticmethod
    def get_by_id(id_):
        """Return the secret code"""
        attr = GK.Attribute.list_new()
        GK.Attribute.list_append_string(attr, 'id', id_)
        result, value = GK.find_items_sync(GK.ItemType.GENERIC_SECRET,
                                           attr)
        if result == GK.Result.OK:
            return value[0].secret
        return None

    @staticmethod
    def insert(id_, secret_code):
        """
        Insert a secret code to Keyring database
        :param id_: the encrypted id
        :param secret_code: the secret code
        """
        GK.create_sync(Keyring.ID, None)
        attr = GK.Attribute.list_new()
        GK.Attribute.list_append_string(attr, 'id', id_)
        GK.Attribute.list_append_string(attr, 'secret_code', secret_code)
        GK.item_create_sync(Keyring.ID, GK.ItemType.GENERIC_SECRET,
                            repr(id), attr, secret_code, False)

    @staticmethod
    def remove(id_):
        """
        Remove an account from Gnome Keyring by secret id
        :param id_: the encrypted secret code.
        :return: bool
        """
        found = False
        (result, ids) = GK.list_item_ids_sync(Keyring.ID)
        gid = None
        for gid in ids:
            (result, item) = GK.item_get_info_sync(Keyring.ID, gid)
            if result == GK.Result.OK and \
                    item.get_display_name().strip("'") == id_:
                found = True
                break
        if found and gid:
            GK.item_delete_sync(Keyring.ID, gid)
