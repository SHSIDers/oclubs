#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""oclubs.shsid.org Clubs."""

from __future__ import absolute_import

from oclubs.access import database
from oclubs.objs.base import BaseObject, Property, ListProperty


class Club(BaseObject):
    table = 'club'
    identifier = 'club_id'
    name = Property('club_name')
    teacher = Property('club_teacher', 'User')
    leader = Property('club_leader', 'User')
    description = Property('club_desc', 'FormattedText')
    location = Property('club_picture')
    is_active = Property('club_inactive', lambda v: not v)
    intro = Property('club_intro')
    picture = Property('club_picture', 'Upload')
    members = ListProperty('club_member', 'cm_club', 'cm_user', 'User')
    all_act = ListProperty('activities', 'act_club', 'act_id', 'Activity')

    _excellentclubs = None

    @property
    def is_excellent(self):
        return self.id in self.excellentclubs()

    @staticmethod
    def excellentclubs():
        if Club._excellentclubs is None:
            # FIXME: BLOCKED-ON-REDIS
            Club._excellentclubs = set()
        return Club._excellentclubs

    @classmethod
    def randomclubs(cls, amount):
        tempdata = database.fetch_onecol(
            cls.table,
            cls.identifier,
            {
                'where': [],
                'order': [('RAND()', True)],
                'limit': amount
            }
        )
        return [cls(item) for item in tempdata]

    def activities(self, types, dates=(True, True)):
        from oclubs.objs import Activity

        return Activity.get_activities_conditions(
            types,
            {
                'where': [('=', 'act_club', self.id)],
                'order': [('act_date', True)]
            },
            dates=dates
        )

    def add_member(self, user):
        database.insert_row('club_member',
                            {'cm_club': self.id, 'cm_user': user.id})
        del self.members

    def remove_member(self, user):
        database.delete_rows('club_member',
                             [('=', 'cm_club', self.id),
                              ('=', 'cm_user', user.id)])
        del self.members
