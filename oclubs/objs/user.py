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
    table = 'user'
    identifier = 'user_id'

    def __init__(self, uid):
        """Initializer."""
        super(User, self).__init__(uid)
        self._picture = self._clubs = None

    @property
    def studentid(self):
        return self._data['studentid']

    @studentid.setter
    def studentid(self, value):
        self._setdata('studentid', 'user_login_name', value)

    @property
    def passportname(self):
        return self._data['passportname']

    @passportname.setter
    def passportname(self, value):
        self._setdata('passportname', 'user_passport_name', value)

    @property
    def nickname(self):
        return self._data['nickname']

    @nickname.setter
    def nickname(self, value):
        self._setdata('nickname', 'user_nick_name', value)

    @property
    def email(self):
        return self._data['email']

    @email.setter
    def email(self, value):
        self._setdata('email', 'user_email', value)

    @property
    def picture(self):
        from oclubs.objs import Upload
        if self._picture is None:
            self._picture = Upload(self._data['picture'])
        return self._picture

    @picture.setter
    def picture(self, value):
        self._picture = value
        self._setdata('picture', 'user_picture', value.id)

    @property
    def type(self):
        return self._data['type']

    @type.setter
    def type(self, value):
        self._setdata('type', 'user_type', value)

    @property
    def gradyear(self):
        return self._data['gradyear']

    @gradyear.setter
    def gradyear(self, value):
        self._setdata('gradyear', 'user_grad_year', value)

    @property
    def password(self):  # write-only
        raise NotImplementedError

    @password.setter
    def password(self, value):
        self._setdata(None, 'user_password', _crypt.encrypt(value))

    @property
    def userpage(self):
        # FIXME: BLOCKED-ON-DATABSE
        pass

    @property
    def clubs(self):
        if self._clubs is None:
            from oclubs.objs import Club

            self._clubs = database.fetch_onecol(
                'club_member',
                [('=', 'cm_user', self.id)],
                'cm_club'
            )
            self._clubs = [Club(club) for club in self._clubs]

        return self._clubs

    @property
    def _data(self):
        """Load data from db."""
        return super(User, self)._data(
            {
                'user_login_name': 'studentid',
                'user_nick_name': 'nickname',
                'user_passport_name': 'passportname',
                'user_picture': 'picture',
                'user_type': 'type',
                'user_grad_year': 'gradyear',
                'user_email': 'email'
            }
        )

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
