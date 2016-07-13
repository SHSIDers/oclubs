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
        self._prop('name', 'club_name')
        self._prop('teacher', 'club_teacher', User)
        self._prop('leader', 'club_leader', User)
        self._prop('description', 'club_desc', FormattedText)
        # FIXME: define location syntax
        self._prop('location', 'club_picture', json)
        self._prop('is_active', 'club_inactive', lambda v: not v)
        self._prop('intro', 'club_intro')
        self._prop('picture', 'club_picture', Upload)
        self._listprop('members', 'club_member', 'cm_club', 'cm_user', User)
        self._listprop('activities', 'activities', 'act_club', 'act_id', Activity)

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
