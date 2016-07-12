#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""oclubs.shsid.org Clubs."""

from __future__ import absolute_import

import json

from oclubs.access import database
from oclubs.objs import FormattedText
from oclubs.objs.base import BaseObject
# from oclubs.objs import Upload


class Club(BaseObject):
    """Club class."""
    table = 'club'
    identifier = 'club_id'
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

    @name.setter
    def name(self, value):
        self._setdata('name', 'club_name', value)

    @property
    def teacher(self):
        from oclubs.objs import User
        if self._teacher is None:
            self._teacher = User(self._data['teacher'])
        return self._teacher

    @teacher.setter
    def teacher(self, value):
        self._teacher = value
        self._setdata('teacher', 'club_teacher', value.id)

    @property
    def leader(self):
        from oclubs.objs import User
        if self._leader is None:
            self._leader = User(self._data['leader'])
        return self._leader

    @leader.setter
    def leader(self, value):
        self._leader = value
        self._setdata('leader', 'club_leader', value.id)

    @property
    def intro(self):
        return self._intro

    @intro.setter
    def intro(self, value):
        self._intro = value
        self._setdata('intro', 'club_intro', value)

    # @property
    # def picture(self):
    #     if self._picture is None:
    #         self._picture = Upload(self._data['picture'])
    #     return self._picture

    # @picture.setter
    # def picture(self, value):
    #     self._picture = value
    #     self._setdata('picture', 'club_pic', value.id)

    @property
    def description(self):
        if self._description is None:
            self._description = FormattedText(self._data['description'])
        return self._description

    @description.setter
    def description(self, value):
        self._description = value
        self._setdata('description', 'club_desc', value.id)

    @property
    def location(self):
        # FIXME: define location syntax
        if self._location is None:
            self._location = json.loads(self._data['location'])
        return self._location

    @location.setter
    def location(self, value):
        # FIXME: As above
        self._location = value
        self._setdata('location', 'club_location', json.dumps(value))

    @property
    def is_active(self):
        return not self._data['inactive']

    @is_active.setter
    def is_active(self, value):
        self._setdata('inactive', 'club_inactive', not value)

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
