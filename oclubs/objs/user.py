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
    table = 'user'
    identifier = 'user_id'

    def __init__(self, uid):
        """Initializer."""
        super(User, self).__init__(uid)

        if self._static_initialize_once():
            return
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
            {'user_password': _crypt.encrypt(value)},
            [('=', self.identifier, self.id)]
        )

    def cas_in_club(self, club):
        return database.fetch_oneentry(
            'attendance',
            'SUM(act_cas)',
            {
                'join': [('inner', 'activity', [('act_id', 'att_act')])],
                'where': [('=', 'att_user', self.id)],
            }
        )

    def activities_reminder(self, *args):
        from oclubs.objs import Activity

        return Activity.get_activities_conditions(
            args,
            {
                'join': [('inner', 'club_member', [('act_club', 'cm_club')])],
                'where': [('=', 'cm_user', self.id)],
                'order': [('act_date', True)]
            },
            require_future=True
        )

    @staticmethod
    def attempt_login(studentid, password):
        try:
            data = database.fetch_onerow(
                'user',
                {'user_id': 'id', 'user_password': 'password'},
                [('=', 'user_login_name', studentid)]
            )
        except NoRow:
            return
        else:
            if _crypt.verify(password, data['password']):
                return User(data['id'])
            else:
                return
