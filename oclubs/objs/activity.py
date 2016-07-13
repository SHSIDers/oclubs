#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""oclubs.shsid.org Activities."""

from __future__ import absolute_import, unicode_literals

from datetime import datetime, date
import json

from oclubs.objs.base import BaseObject


class Activity(BaseObject):
    _propsdb = {}
    table = 'activity'
    identifier = 'act_id'
    date_fmtstr = '%Y%m%d'

    def __init__(self, aid):
        super(Activity, self).__init__(aid)

        if self._static_initialize_once():
            return
        from oclubs.objs import Club, FormattedText, User
        self._prop('club', 'act_club', Club)
        self._prop('description', 'act_desc', FormattedText)
        self._prop('date', 'act_date', (
            lambda val: datetime.strptime(str(val), self.date_fmtstr).date(),
            lambda val: int(val.strftime(self.date_fmtstr)),
        ))
        self._prop('time', 'act_time')
        # FIXME: define location syntax
        self._prop('location', 'act_location', json)
        self._prop('cas', 'act_cas')
        self.post = None  # FIXME: Post object
        self._listprop('attendance', 'attendance', 'att_act', 'att_user', User)

    @property
    def ongoing_or_future(self):
        return self.datetime >= date.today()
