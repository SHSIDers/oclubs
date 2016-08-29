#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

import re
from datetime import date
from flask_login import UserMixin
from passlib.context import CryptContext
from xkcdpass import xkcd_password as xp

from oclubs.access import database, email, redis
from oclubs.enums import UserType
from oclubs.exceptions import NoRow, PasswordTooShort
from oclubs.objs.activity import int_date
from oclubs.objs.base import BaseObject, Property, ListProperty, paged_db_read


_crypt = CryptContext(schemes=['bcrypt'])  # , 'sha512_crypt', 'pbkdf2_sha512'
_words = xp.generate_wordlist(wordfile=xp.locate_wordfile())


def _encrypt(passwd):
    if len(passwd) < 6:
        raise PasswordTooShort
    return _crypt.encrypt(passwd)


class User(BaseObject, UserMixin):
    table = 'user'
    identifier = 'user_id'
    studentid = Property('user_login_name')
    passportname = Property('user_passport_name')
    password = Property('user_password', (NotImplemented, _encrypt))
    nickname = Property('user_nick_name', rediscached=True)
    email = Property('user_email')
    phone = Property('user_phone')
    picture = Property('user_picture', 'Upload')
    type = Property('user_type', UserType)
    grade = Property('user_grade')
    currentclass = Property('user_class')
    clubs = ListProperty('club_member', 'cm_user', 'cm_club', 'Club')

    GRADECLASSREGEX = re.compile(r'^\s*(\d+)\s*[-_/\\]\s*(\d+)\s*$')

    @property
    def grade_and_class(self):
        # %d cannot accept None
        return '%s - %s' % (self.grade, self.currentclass)

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
        if self.email and '@' in self.email:
            email.send((self.email, self.passportname), title, contents)

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
        pager_fetch, pager_return = pager
        ret = pager_fetch(
            database.fetch_multirow,
            'notification',
            {
                'notification_text': 'text',
                'notification_isread': 'isread',
                'notification_date': 'date'
            },
            {
                'where': [('=', 'notification_user', self.id)],
                'order': [('notification_date', False)]
            }
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

    def get_invitation(self):
        from oclubs.objs import Club

        ret = database.fetch_multirow(
                'invitation',
                {'invitation_club': 'club', 'invitation_date': 'date'},
                {'invitation_user': self.id}
            )
        for item in ret:
            item['date'] = int_date(item['date'])
            item['club'] = Club(item['club'])
        return ret

    def delete_invitation(self, club):
        try:
            database.delete_rows(
                'invitation',
                {'invitation_club': club.id, 'invitation_user': self.id}
            )
        except NoRow:
            pass

    @classmethod
    def attempt_login(cls, studentid, password):
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
                return cls(data['id'])
            else:
                return

    @classmethod
    def find_user(cls, gradeclass, passportname):
        reobj = cls.GRADECLASSREGEX.match(gradeclass)
        if not reobj:
            return

        grade, currentclass = reobj.group(1), reobj.group(2)

        try:
            return cls(database.fetch_oneentry(
                'user',
                'user_id',
                {
                    'user_grade': grade,
                    'user_class': currentclass,
                    'user_passport_name': passportname
                }
            ))
        except NoRow:
            return

    @classmethod
    def find_teacher(cls, emailaddress):
        try:
            return cls(database.fetch_oneentry(
                'user',
                'user_id',
                {
                    'user_email': emailaddress,
                    'user_type': UserType.TEACHER.value
                }
            ))
        except NoRow:
            return

    @classmethod
    def allusers(cls, non_teachers=False):
        conds = []
        if non_teachers:
            conds.append(('!=', 'user_type', UserType.TEACHER.value))

        tempdata = database.fetch_onecol(
            cls.table,
            cls.identifier,
            conds
        )
        return [cls(item) for item in tempdata]

    @classmethod
    def get_new_passwords(cls):
        return [(
            cls(int(key.split(':')[-1])),
            redis.RedisCache(key).detach().get()
        ) for key in redis.r.keys('tempuserpw:*')]

    @staticmethod
    def generate_password():
        return xp.generate_xkcdpassword(_words)
