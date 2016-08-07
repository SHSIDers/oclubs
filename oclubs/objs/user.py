#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

from datetime import date
from flask_login import UserMixin
from passlib.context import CryptContext
from xkcdpass import xkcd_password as xp

from oclubs.access import database, email
from oclubs.enums import UserType
from oclubs.exceptions import NoRow
from oclubs.objs.base import BaseObject, Property, ListProperty, paged_db_read

_crypt = CryptContext(schemes=['bcrypt'])  # , 'sha512_crypt', 'pbkdf2_sha512'
_words = xp.generate_wordlist(wordfile=xp.locate_wordfile())


class User(BaseObject, UserMixin):
    table = 'user'
    identifier = 'user_id'
    studentid = Property('user_login_name')
    passportname = Property('user_passport_name')
    password = Property('user_password', (NotImplemented, _crypt.encrypt))
    nickname = Property('user_nick_name', rediscached=True)
    email = Property('user_email')
    phone = Property('user_phone')
    picture = Property('user_picture', 'Upload')
    type = Property('user_type', UserType)
    grade = Property('user_grade')
    currentclass = Property('user_class')
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

    def email_user(self, title, contents):
        address = self.email or 'root@localhost'
        email.send((address, self.passportname), title, contents)

    def notify_user(self, contents):
        from oclubs.objs.activity import date_int
        database.insert_row(
            'notification',
            {
                'notification_user': self.id,
                'notification_text': contents,
                'notification_isread': False,
                'notification_date': date_int(date.today())
            }
        )

    @paged_db_read
    def get_notifications(self, pager):
        from oclubs.objs.activity import int_date

        pager_fetch, pager_return = pager
        ret = pager_fetch(
            database.fetch_multirow,
            'notification',
            {
                'notification_text': 'text',
                'notification_isread': 'isread',
                'notification_date': 'date'
            },
            {'notification_user': self.id}
        )
        for item in ret:
            item['date'] = int_date(item['date'])

        return pager_return(ret)

    def set_notifications_readall(self):
        try:
            database.update_row(
                'notification',
                {'notification_isread': True},
                {'notification_user': self.id}
            )
        except NoRow:
            pass

    def get_unread_notifications_num(self):
        return database.fetch_oneentry(
            'notification',
            database.RawSQL('COUNT(*)'),
            {'notification_user': self.id, 'notification_isread': False}
        )

    @staticmethod
    def attempt_login(studentid, password):
        def emptypw():
            # to gave some delay, verify empty password and discard the results
            _crypt.verify(
                password,
                '$2a$12$mf04JOZtIxRtPFw793AGyeYGHGuiN2ikL/HO9fEKdCIilJqwRZKg.'
            )

        if not password:
            emptypw()
            return

        try:
            data = database.fetch_onerow(
                'user',
                {'user_id': 'id', 'user_password': 'password'},
                {'user_login_name': studentid}
            )
        except NoRow:
            emptypw()
            return
        else:
            if not data['password']:
                emptypw()
                return
            elif _crypt.verify(password, data['password']):
                return User(data['id'])
            else:
                return

    @staticmethod
    def find_user(studentid, passportname):
        try:
            return User(database.fetch_oneentry(
                'user',
                'user_id',
                {
                    'user_login_name': studentid,
                    'user_passport_name': passportname
                }
            ))
        except NoRow:
            return

    @classmethod
    def allusers(cls):
        tempdata = database.fetch_onecol(
            cls.table,
            cls.identifier,
            []
        )
        return [cls(item) for item in tempdata]

    @staticmethod
    def generate_password():
        return xp.generate_xkcdpassword(_words)
