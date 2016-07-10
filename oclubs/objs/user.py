#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""oclubs.shsid.org Users."""

from __future__ import absolute_import

from passlib.context import CryptContext

from oclubs.access import database
from oclubs.exceptions import NoRow
from oclubs.objs.base import BaseObject

_crypt = CryptContext(schemes=['bcrypt'])  # , 'sha512_crypt', 'pbkdf2_sha512'


class User(BaseObject):
    """User class."""

    def __init__(self, uid):
        """Initializer."""
        super(User, self).__init__(uid)

    def count_cas(club, time):
        # TODO
        pass

    @property
    def username(self):
        return self._data['username']

    @property
    def userpage(self):
        # FIXME: BLOCKED-ON-DATABSE
        pass

    @property
    def _data(self):
        """Load data from db."""
        return super(User, self)._data(
            'user',
            [('=', 'user_id', self.id)],
            {
                'user_login_name': 'username',
                'user_nick_name': 'nickname',
                'user_type': 'type',
                'user_grad_year': 'gradyear'
            }
        )

    @staticmethod
    def attempt_login(username, password):
        try:
            data = database.fetch_onerow(
                'user',
                [('=', 'user_login_name', username)],
                {
                    'user_id': 'id',
                    'user_password': 'password'
                }
            )
        except NoRow:
            return
        else:
            if _crypt.verify(password, data['password']):
                return User(data['id'])
            else:
                return
