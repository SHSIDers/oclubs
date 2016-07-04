#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""oclubs.shsid.org Users."""

from __future__ import absolute_import

from oclubs.objs.base import BaseObject


class User(BaseObject):
    """User class."""

    def __init__(self, uid):
        """Initializer."""
        super(User, self).__init__(uid)

    def attempt_login(self, pw):
        # TODO
        pass

    def count_cas(club, time):
        # TODO
        pass

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