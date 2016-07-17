#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""oclubs.shsid.org Users."""

from __future__ import absolute_import

from passlib.context import CryptContext

from oclubs.access import database
from oclubs.exceptions import NoRow
from oclubs.objs.base import BaseObject, Property, ListProperty

_crypt = CryptContext(schemes=['bcrypt'])  # , 'sha512_crypt', 'pbkdf2_sha512'


class User(BaseObject):
    table = 'user'
    identifier = 'user_id'
    studentid = Property('user_login_name')
    passportname = Property('user_passport_name')
    password = Property('user_password', (NotImplemented, _crypt.encrypt))
    nickname = Property('user_nick_name')
    email = Property('user_email')
    phone = Property('user_phone')
    picture = Property('user_picture', 'Upload')
    type = Property('user_type')
    gradyear = Property('user_grad_year')
    clubs = ListProperty('club_member', 'cm_user', 'cm_club', 'Club')

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
