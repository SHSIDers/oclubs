#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#


"""oclubs.shsid.org Activities."""

from __future__ import absolute_import, unicode_literals

import json

from oclubs.access import database
from oclubs.objs.base import BaseObject


class Activity(BaseObject):
    table = 'activity'
    identifier = 'act_id'

    def __init__(self, aid):
        super(Activity, self).__init__(aid)
        self._club = self._description = None
        self._date = self._location = None
        self._post = self._attendance = None

    @property
    def club(self):
        from oclubs.objs import Club
        if self._club is None:
            self._club = Club(self._data['club'])
        return self._club

    @club.setter
    def club(self, value):
        self._club = value
        self._setdata('club', 'act_club', value.id)

    @property
    def description(self):
        from oclubs.objs import FormattedText
        if self._description is None:
            self._description = FormattedText(self._data['description'])
        return self._description

    @description.setter
    def description(self, value):
        self._description = value
        self._setdata('description', 'act_desc', value.id)

    @property
    def date(self):
        # FIXME: define date object
        if self._date is None:
            self._date = self._data['date']
        return self._date

    @date.setter
    def date(self, value):
        # FIXME: As above
        self._location = value
        self._setdata('location', 'act_date', value)

    @property
    def time(self):
        return self._data['time']

    @time.setter
    def time(self, value):
        self._setdata('time', 'act_time', value)

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
        self._setdata('location', 'act_location', json.dumps(value))

    @property
    def cas(self):
        return self._data['cas']

    @cas.setter
    def cas(self, value):
        self._setdata('cas', 'act_cas', value)

    # FIXME: Post object

    @property
    def attendance(self):
        if self._attendance is None:
            from oclubs.objs import User

            self._attendance = database.fetch_onecol(
                'attendance',
                [('=', 'att_act', self.id)],
                'att_user'
            )
            self._attendance = [User(member) for member in self._members]

        return self._attendance

    @property
    def _data(self):
        return super(Activity, self)._data(
                {
                    'act_name': 'name',
                    'act_club': 'club',
                    'act_desc': 'description',
                    'act_date': 'date',
                    'act_time': 'time',
                    'act_location': 'location',
                    'act_cas': 'cas',
                    'act_cp': 'post',
                }
            )
