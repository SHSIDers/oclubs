#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""oclubs.shsid.org Clubs."""

from __future__ import absolute_import

from oclubs.access import database


class Club(object):
    """Club class."""

    def __init__(self, cid):
        """Initializer."""
        super(Club, self).__init__()
        self.cid = cid
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

    def reg_hm(student, time, comments):
        pass
    def reg_act(student, activity):
        pass
    def change_leader(student):
        pass
    def attend(student, time):
        pass
    def evaluate(student):
        pass
    def memberinfo():
        pass
    def join_club(student):
        pass
    def quit_club(student, comments):
        pass
