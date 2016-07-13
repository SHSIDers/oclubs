#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#


"""oclubs.shsid.org Activities."""

from __future__ import absolute_import, unicode_literals

import json

from oclubs.objs.base import BaseObject


class Activity(BaseObject):
    _propsdb = {}
    _props = {}
    table = 'activity'
    identifier = 'act_id'

    def __init__(self, aid):
        super(Activity, self).__init__(aid)

        from oclubs.objs import Club, FormattedText, User
        self.club = self._prop('act_club', 'club', Club)
        self.description = self._prop('act_desc', 'description', FormattedText)
        # FIXME: define date object
        self.date = self._prop('act_date', 'date')
        self.time = self._prop('act_time', 'time')
        # FIXME: define location syntax
        self.location = self._prop('act_location', 'location', json)
        self.cas = self._prop('act_cas', 'cas')
        self.post = None  # FIXME: Post object
        self.attendance = self._listprop('attendance', 'att_act', 'att_user', 'attendance', User)
