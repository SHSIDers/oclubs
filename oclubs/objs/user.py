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
    _propsdb = {}
    _props = {}
    table = 'user'
    identifier = 'user_id'

    def __init__(self, uid):
        """Initializer."""
        super(User, self).__init__(uid)

        from oclubs.objs import Club, Upload
        self._prop('studentid', 'user_login_name')
        self._prop('passportname', 'user_passport_name')
        self._prop('nickname', 'user_nick_name')
        self._prop('email', 'user_email')
        self._prop('phone', 'user_phone')
        self._prop('picture', 'user_picture', Upload)
        self._prop('type', 'user_type')
        self._prop('gradyear', 'user_grad_year')
        self._listprop('clubs', 'club_member', 'cm_user', 'cm_club', Club)

    @property
    def password(self):  # write-only
        raise NotImplementedError

    @password.setter
    def password(self, value):
        database.update_row(
            self.table,
            [('=', self.identifier, self.id)],
            {'user_password': _crypt.encrypt(value)}
        )

    @property
    def userpage(self):
        # FIXME: BLOCKED-ON-DATABSE
        pass

    @staticmethod
    def attempt_login(studentid, password):
        try:
            data = database.fetch_onerow(
                'user',
                [('=', 'user_login_name', studentid)],
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
