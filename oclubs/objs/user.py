#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""oclubs.shsid.org Users."""

from __future__ import absolute_import

from oclubs.access import database


class User(object):
    """User class."""

    def __init__(self, uid):
        """Initializer."""
        super(User, self).__init__()
        self.uid = uid
        self.data = {}

    def load_db(self):
        """Load data from db."""
        self.data = database.fetch_onerow(
            'user',
            [('=', 'user_id', self.uid)],
            {
                'user_login_name': 'username',
                'user_nick_name': 'nickname',
                'user_type': 'type',
                'user_grad_year': 'gradyear'
            }
        )

    def attempt_login(self, pw):
        