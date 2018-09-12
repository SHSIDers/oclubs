#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals, division

import re
from datetime import date
from flask_login import UserMixin
from passlib.context import CryptContext
from xkcdpass import xkcd_password as xp
import uuid

from oclubs.utils.dates import int_to_dateobj, dateobj_to_int
from oclubs.access import database, email, redis
from oclubs.enums import UserType
from oclubs.exceptions import NoRow, PasswordTooShort
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
    gnumber_id = Property('user_gnumber_id')
    short_id = Property('user_short_id')
    passportname = Property('user_passport_name')
    password = Property('user_password', (NotImplemented, _encrypt))
    nickname = Property('user_nick_name', rediscached=True)
    initalized = Property('user_initalized', bool)
    email = Property('user_email')
    phone = Property('user_phone')
    picture = Property('user_picture', 'Upload')
    type = Property('user_type', UserType)
    grade = Property('user_grade')
    currentclass = Property('user_class')
    clubs = ListProperty('club_member', 'cm_user', 'cm_club', 'Club')
    attendance = ListProperty('attendance', 'att_user', 'att_act', 'Activity')

    GRADECLASSREGEX = re.compile(
        r'^\s*(\d+)(?:\s*[(-_/\\]\s*|\s+)(\d+)\s*(?:\)\s*)?(?:[AB]\s*)?$')

    PREFERENCES = {
        'receive_email': (lambda x: bool(int(x)), True),
    }

    @property
    def callsign(self):
        return str(self.id)

    @property
    def grade_and_class(self):
        # %d cannot accept None
        return '%s(%s)' % (self.grade, self.currentclass)

    @property
    def is_disabled(self):
        return not self._data['password']

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
        if self.is_disabled:
            return

        if self.email and '@' in self.email \
                and self.get_preference('receive_email'):
            email.send((self.email, self.passportname), title, contents)

    def notify_user(self, contents):
        if self.is_disabled:
            return

        database.insert_row(
            'notification',
            {
                'notification_user': self.id,
                'notification_text': contents,
                'notification_isread': False,
                'notification_date': dateobj_to_int(date.today())
            }
        )

    def get_preference(self, name):
        typ, default = self.PREFERENCES[name]

        try:
            ret = database.fetch_oneentry(
                'preferences',
                'pref_value',
                {'pref_user': self.id, 'pref_type': name}
            )
        except NoRow:
            return default
        else:
            return typ(ret)

    def set_preference(self, name, value):
        # we don't set preferences when it is unnecessary,
        # so users can keep a "default" state
        if value == self.get_preference(name):
            return

        update = {'pref_value': value}
        insert = {'pref_user': self.id, 'pref_type': name}
        insert.update(update)
        database.insert_or_update_row('preferences', insert, update)

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
            item['date'] = int_to_dateobj(item['date'])

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
        noti = database.fetch_oneentry(
            'notification',
            database.RawSQL('COUNT(*)'),
            {'notification_user': self.id, 'notification_isread': False}
        )
        invi = database.fetch_oneentry(
            'invitation',
            database.RawSQL('COUNT(*)'),
            {'invitation_user': self.id}
        )
        return noti + invi

    def get_invitation(self):
        from oclubs.objs import Club

        ret = database.fetch_multirow(
                'invitation',
                {'invitation_club': 'club', 'invitation_date': 'date'},
                {'invitation_user': self.id}
            )
        for item in ret:
            item['date'] = int_to_dateobj(item['date'])
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
    def attempt_login(cls, username, password):
        def emptypw():
            # to gave some delay, verify empty password and discard the results
            _crypt.verify(
                password,
                '$2a$12$mf04JOZtIxRtPFw793AGyeYGHGuiN2ikL/HO9fEKdCIilJqwRZKg.'
            )

        if not password:
            emptypw()
            return

        data = database.fetch_multirow(
            'user',
            {'user_id': 'id', 'user_password': 'password'},
            {'user_login_name': username}
        )

        if not data:
            emptypw()
            return

        else:
            for d in data:
                if not d['password']:
                    emptypw()
                    continue
                elif _crypt.verify(password, d['password']):
                    return cls(d['id'])
                else:
                    continue
            else:
                emptypw()
                return

    @classmethod
    def extract_gradeclass(cls, gradeclass):
        reobj = cls.GRADECLASSREGEX.match(gradeclass)
        if not reobj:
            raise ValueError

        return int(reobj.group(1)), int(reobj.group(2))

    @classmethod
    def find_user(cls, gradeclass, passportname):
        try:
            grade, currentclass = cls.extract_gradeclass(gradeclass)
        except ValueError:
            return

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
            # Dynamically create a new teacher
            from oclubs.objs import Upload

            ret = cls.new()
            ret.studentid = emailaddress
            ret.passportname = emailaddress
            ret.password = None
            ret.nickname = emailaddress
            ret.email = emailaddress
            ret.phone = None
            ret.picture = Upload(-101)
            ret.type = UserType.TEACHER
            ret.grade = None
            ret.currentclass = None
            ret.initalized = False

            return ret.create()

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
    def get_userobj_from_passportname(cls, passportname):
        allusers = cls.allusers()
        for user in allusers:
            if user.passportname == passportname:
                return user

        return None


    @classmethod
    def get_userobj_from_loginname(cls, loginname):
        allusers = cls.allusers()
        for user in allusers:
            if user.studentid == loginname:
                return user

        return None

    @classmethod
    def get_new_passwords(cls):
        return [(
            cls(int(key.split(':')[-1])),
            redis.RedisCache(key, 0).detach().get()
        ) for key in redis.r.keys('tempuserpw:*')]

    @staticmethod
    def generate_password():
        return xp.generate_xkcdpassword(_words)

    @staticmethod
    def new_reset_request(userObj):
        '''Creates a new pending reset'''
        reset_request_id = uuid.uuid4().hex

        reset_request = redis.RedisCache('reset_request:' + reset_request_id,
                                         1800)
        reset_request.set(userObj.callsign)

        return reset_request_id

    @staticmethod
    def get_reset_request(tokenStr):
        '''Return user callsign from reset token'''
        return redis.RedisCache(
            'reset_request:' + tokenStr, 1800).detach().get()
