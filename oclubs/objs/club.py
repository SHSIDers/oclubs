#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

from oclubs.access import database
from oclubs.enums import ClubType, UserType
from oclubs.objs.base import BaseObject, Property, ListProperty


class Club(BaseObject):
    table = 'club'
    identifier = 'club_id'
    name = Property('club_name')
    teacher = Property('club_teacher', 'User')
    leader = Property('club_leader', 'User')
    description = Property('club_desc', 'FormattedText')
    location = Property('club_location')
    is_active = Property('club_inactive', lambda v: not v)
    intro = Property('club_intro')
    picture = Property('club_picture', 'Upload')
    type = Property('club_type', ClubType)
    members = ListProperty('club_member', 'cm_club', 'cm_user', 'User')
    all_act = ListProperty('activities', 'act_club', 'act_id', 'Activity')

    _excellentclubs = None

    @property
    def is_excellent(self):
        return self.id in self.excellentclubs()

    @property
    def members_num(self):
        num = 0
        for member in self.members:
            num += 1
        return num

    @staticmethod
    def excellentclubs():
        if Club._excellentclubs is None:
            # FIXME: BLOCKED-ON-REDIS
            Club._excellentclubs = Club.randomclubs(10)
        return Club._excellentclubs

    @classmethod
    def randomclubs(cls, amount, types=None):
        where = []
        if types:
            types = [_type.value for _type in types]
            where.append(('in', 'club_type', types))
        tempdata = database.fetch_onecol(
            cls.table,
            cls.identifier,
            {
                'where': where,
                'order': [(database.RawSQL('RAND()'), True)],
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
            },
            dates=dates,
            order_by_time=True
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

    @classmethod
    def get_clubs_special_access(cls, user):
        if user.type == UserType.STUDENT:
            ret = database.fetch_onecol(
                cls.table,
                cls.identifier,
                {'club_leader': user.id},
            )
        elif user.type == UserType.TEACHER:
            ret = database.fetch_onecol(
                cls.table,
                cls.identifier,
                {'club_teacher': user.id},
            )
        else:  # ADMIN
            ret = []

        return map(cls, ret)
