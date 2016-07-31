#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

import random

from oclubs.access import database, redis
from oclubs.enums import ClubType, UserType
from oclubs.objs.base import BaseObject, Property, ListProperty


class Club(BaseObject):
    table = 'club'
    identifier = 'club_id'
    name = Property('club_name', search=True)
    teacher = Property('club_teacher', 'User')
    leader = Property('club_leader', 'User')
    description = Property('club_desc', 'FormattedText', search=True)
    location = Property('club_location')
    is_active = Property('club_inactive', lambda v: not v)
    intro = Property('club_intro', search=True)
    picture = Property('club_picture', 'Upload')
    type = Property('club_type', ClubType)
    members = ListProperty('club_member', 'cm_club', 'cm_user', 'User')
    all_act = ListProperty('activities', 'act_club', 'act_id', 'Activity')

    @property
    def is_excellent(self):
        return self in self.excellentclubs()

    @property
    def members_num(self):
        num = 0
        for member in self.members:
            num += 1
        return num

    # We can't use @property because fails with Club.excellentclubs = []
    @classmethod
    def excellentclubs(cls, amount=None):
        ret = [cls(item) for item in redis.RedisList('excellentclubs', -1)]
        if amount:
            amount = min(len(ret), amount)
            return random.sample(ret, amount)
        return ret

    @staticmethod
    def set_excellentclubs(newval):
        newval = [item.id for item in newval]
        lst = redis.RedisList('excellentclubs', -1)
        lst[:] = newval

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

    @classmethod
    def allclubs(cls, types=None):
        where = []
        if types:
            types = [_type.value for _type in types]
            where.append(('in', 'club_type', types))
        tempdata = database.fetch_onecol(
            cls.table,
            cls.identifier,
            {
                'where': where,
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
                             {'cm_club': self.id, 'cm_user': user.id})
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
