#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""oclubs.shsid.org Clubs."""

from __future__ import absolute_import

import json

from oclubs.access import database
from oclubs.objs import FormattedText
from oclubs.objs.base import BaseObject


class Club(BaseObject):
    """Club class."""
    _excellentclubs = None

    def __init__(self, cid):
        """Initializer."""
        super(Club, self).__init__()
        self._teacher = self._leader = None
        self._description = self._location = None
        self._activities = self._members = None

    @property
    def name(self):
        return self._data['name']

    @property
    def teacher(self):
        from oclubs.objs import User
        if self._teacher is None:
            self._teacher = User(self._data['teacher'])
        return self._teacher

    @property
    def leader(self):
        from oclubs.objs import User
        if self._leader is None:
            self._leader = User(self._data['leader'])
        return self._leader

    @property
    def description(self):
        if self._description is None:
            self._description = FormattedText(self._data['description'])
        return self._description

    @property
    def location(self):
        # FIXME: define location syntax
        if self._location is None:
            self._location = json.loads(self._data['location'])
        return self._location

    @property
    def is_active(self):
        return not self._data['inactive']

    @property
    def is_excellent(self):
        return self.id in self.excellentclubs()

    @property
    def members(self):
        if self._members is None:
            from oclubs.objs import User

            self._members = database.fetch_onecol(
                'club_member',
                [('=', 'cm_club', self.id)],
                'cm_user'
            )
            self._members = [User(member) for member in self._members]

        return self._members

    @property
    def activities(self):
        if self._activities is None:
            from oclubs.objs import Activity

            self._activities = database.fetch_onecol(
                'activity',
                [('=', 'act_club', self.id)],
                'act_id'
            )
            self._activities = [Activity(member) for member in self._members]

        return self._activities

    @property
    def _data(self):
        """Load data from db."""
        return super(Club, self)._data(
            'club',
            [('=', 'club_id', self.id)],
            {
                'club_name': 'name',
                'club_teacher': 'teacher',
                'club_leader': 'leader',
                'club_desc': 'description',
                'club_location': 'location',
                'club_inactive': 'inactive'
            }
        )

    @staticmethod
    def excellentclubs():
        if Club._excellentclubs is None:
            # FIXME: BLOCKED-ON-REDIS
            Club._excellentclubs = set()
        return Club._excellentclubs

    @staticmethod
    def randomclubs(amount):
        # DO NOT ORDER BY RAND() -- slow
        # TODO: ASSERT number of rows < amount

        # FIXME: BLOCKED-ON-DATABASE: JOIN REQUIRED
        return [Club(0)] * 10
