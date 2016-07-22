#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

from flask_login import UserMixin
from passlib.context import CryptContext

from oclubs.access import database
from oclubs.enums import UserType
from oclubs.exceptions import NoRow
from oclubs.objs.base import BaseObject, Property, ListProperty

_crypt = CryptContext(schemes=['bcrypt'])  # , 'sha512_crypt', 'pbkdf2_sha512'


class User(BaseObject, UserMixin):
    table = 'user'
    identifier = 'user_id'
    studentid = Property('user_login_name')
    passportname = Property('user_passport_name')
    password = Property('user_password', (NotImplemented, _crypt.encrypt))
    nickname = Property('user_nick_name')
    email = Property('user_email')
    phone = Property('user_phone')
    picture = Property('user_picture', 'Upload')
    type = Property('user_type', UserType)
    gradyear = Property('user_grad_year')
    clubs = ListProperty('club_member', 'cm_user', 'cm_club', 'Club')

    def cas_in_club(self, club):
        return database.fetch_oneentry(
            'attendance',
            database.RawSQL('SUM(act_cas)'),
            {
                'join': [('inner', 'activity', [('act_id', 'att_act')])],
                'where': [('=', 'att_user', self.id)],
            }
        ) or 0

    def activities_reminder(self, types, signedup_only=False):
        from oclubs.objs import Activity

        if signedup_only:
            return Activity.get_activities_conditions(
                types,
                {
                    'join': [('inner', 'signup',
                             [('act_id', 'signup_act')])],
                    'where': [('=', 'signup_user', self.id)]
                },
                dates=(False, True),
                order_by_time=True
            )
        else:
            return Activity.get_activities_conditions(
                types,
                {
                    'join': [('inner', 'club_member',
                             [('act_club', 'cm_club')])],
                    'where': [('=', 'cm_user', self.id)]
                },
                dates=(False, True),
                order_by_time=True
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
            # to gave some delay, verify empty password and discard the results
            _crypt.verify(
                password,
                '$2a$12$mf04JOZtIxRtPFw793AGyeYGHGuiN2ikL/HO9fEKdCIilJqwRZKg.'
            )
            return
        else:
            if _crypt.verify(password, data['password']):
                return User(data['id'])
            else:
                return
