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
require_version("Gtk", "3.0")
from gi.repository import Gtk

from .row import AccountRow
from ...models import Database, Account


class AccountsList(Gtk.ListBox):
	"""Accounts List."""

	# Default instance of accounts list
	instance = None

	def __init__(self):
		Gtk.ListBox.__init__(self)
		self.set_selection_mode(Gtk.SelectionMode.NONE)
		self.connect("row-activated", self._on_row_activated)
		self.get_style_context().add_class("applications-list")

		self.__fill_data()

	@staticmethod
	def get_default():
		"""Return the default instance of AccountsList."""
		if AccountsList.instance is None:
			AccountsList.instance = AccountsList()
		return AccountsList.instance

	def __fill_data(self):
		"""Fill the Accounts List with accounts."""
		accounts = Database.get_default().accounts
		for account in accounts:
			self.add(AccountRow(Account(account)))

	def _on_row_activated(self, accounts_list, account_row):
		"""On row activated signal override."""
		account_row.toggle_secret_code()