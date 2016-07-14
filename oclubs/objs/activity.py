#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""oclubs.shsid.org Activities."""

from __future__ import absolute_import, unicode_literals

from datetime import datetime, date
import json

from oclubs.access import database
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
        self._prop('date', 'act_date', (self.int_date, self.date_int))
        self._prop('time', 'act_time')
        # FIXME: define location syntax
        self._prop('location', 'act_location', json)
        self._prop('cas', 'act_cas')
        self.post = None  # FIXME: Post object
        self._listprop('attendance', 'attendance', 'att_act', 'att_user', User)

    @property
    def ongoing_or_future(self):
        return self.datetime >= date.today()

    @staticmethod
    def int_date(dateint):
        return datetime.strptime(str(dateint), Activity.date_fmtstr).date()

    @staticmethod
    def date_int(dateobj):
        return int(dateobj.strftime(Activity.date_fmtstr))

    def signup(self, user, concentform=False):
        database.insert_or_update_row(
            'signup',
            {'signup_act': self.id, 'signup_user': user.id,
                'signup_consentform': concentform},
            {'signup_consentform': concentform}
        )
