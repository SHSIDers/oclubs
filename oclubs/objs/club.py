#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""oclubs.shsid.org Clubs."""

from __future__ import absolute_import

import json

from oclubs.objs.base import BaseObject


class Club(BaseObject):
    _propsdb = {}
    _props = {}
    table = 'club'
    identifier = 'club_id'
    _excellentclubs = None

    def __init__(self, cid):
        """Initializer."""
        super(Club, self).__init__(cid)

        from oclubs.objs import Activity, FormattedText, User, Upload
        self.name = self._prop('club_name', 'name')
        self.teacher = self._prop('club_teacher', 'teacher', User)
        self.leader = self._prop('club_leader', 'leader', User)
        self.description = self._prop('club_desc', 'description', FormattedText)
        # FIXME: define location syntax
        self.location = self._prop('club_picture', 'location', json)
        self.is_active = self._prop('club_inactive', 'inactive', lambda v: not v)
        self.intro = self._prop('club_intro', 'intro')
        self.picture = self._prop('club_picture', 'picture', Upload)
        self.members = self._listprop('club_member', 'cm_club', 'cm_user', 'members', User)
        self.activities = self._listprop('activities', 'act_club', 'act_id', 'activities', Activity)

    @property
    def is_excellent(self):
        return self.id in self.excellentclubs()

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
