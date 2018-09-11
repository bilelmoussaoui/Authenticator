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
import gnupg
from .settings import Settings


class GPG(gnupg.GPG):
    instance = None

    def __init__(self):
        gnupg.GPG.__init__(self, gnupghome=Settings.get_default().gpg_location)

    @staticmethod
    def get_default():
        if GPG.instance is None:
            GPG.instance = GPG()
        return GPG.instance

    def get_keys(self):
        return {
            "public": self.list_keys(),
            "private": self.list_keys(True)
        }

    def decrypt_json(self, filename, paraphrase, out_file):
        with open(filename, 'rb') as infile:
            status = self.decrypt_file(infile, passphrase=paraphrase, output=out_file)
        return status

    def ecrypt_json(self, json_obj, fingerprint):
        return self.encrypt(json_obj, recipients=fingerprint)
