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
        self._prop('club', 'act_club', Club)
        self._prop('description', 'act_desc', FormattedText)
        # FIXME: define date object
        self._prop('date', 'act_date')
        self._prop('time', 'act_time')
        # FIXME: define location syntax
        self._prop('location', 'act_location', json)
        self._prop('cas', 'act_cas')
        self.post = None  # FIXME: Post object
        self._listprop('attendance', 'attendance', 'att_act', 'att_user', User)
