#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""oclubs.shsid.org Activities."""

from __future__ import absolute_import, unicode_literals

from datetime import datetime, date
import json

from oclubs.access import database
from oclubs.objs.base import BaseObject, Property, ListProperty


def int_date(dateint):
    return datetime.strptime(str(dateint), Activity.date_fmtstr).date()


def date_int(dateobj):
    return int(dateobj.strftime(Activity.date_fmtstr))


class Activity(BaseObject):
    table = 'activity'
    identifier = 'act_id'
    name = Property('act_name')
    club = Property('act_club', 'Club')
    description = Property('act_desc', 'FormattedText')
    date = Property('act_date', (int_date, date_int))
    time = Property('act_time')
    # FIXME: define location syntax
    location = Property('act_location', json)
    cas = Property('act_cas')
    post = None  # FIXME: Post object
    attendance = ListProperty('attendance', 'att_act', 'att_user', 'User')

    date_fmtstr = '%Y%m%d'

    @property
    def ongoing_or_future(self):
        return self.datetime >= date.today()

    def signup(self, user, concentform=False):
        database.insert_or_update_row(
            'signup',
            {'signup_act': self.id, 'signup_user': user.id,
                'signup_consentform': concentform},
            {'signup_consentform': concentform}
        )

    @classmethod
    def get_activities_conditions(cls, times, additional_conds=None,
                                  require_future=False):
        times = [time[0] for time in filter(
            lambda val: val[1], enumerate(times))]

        conds = {}
        if additional_conds:
            conds.update(additional_conds)

        conds['where'] = conds.get('where', [])
        if require_future:
            conds['where'].append('>=', 'act_date', date_int(date.today()))
        conds['where'].append(('in', 'act_time', times))

        acts = database.fetch_onecol(
            'activity',
            'act_id',
            conds
        )

        return [cls(act) for act in acts]
