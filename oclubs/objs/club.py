#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

from datetime import date
import random

from oclubs.access import database, redis
from oclubs.enums import ClubType, UserType, ClubJoinMode
from oclubs.objs.base import BaseObject, Property, ListProperty, paged_db_read


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
    joinmode = Property('club_joinmode', ClubJoinMode)
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
    def randomclubs(cls, amount, types=None, active_only=True):
        where = []
        if types:
            types = [_type.value for _type in types]
            where.append(('in', 'club_type', types))
        if active_only:
            where.append(('=', 'club_inactive', False))
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
    @paged_db_read
    def allclubs(cls, types=None, active_only=True, pager=None):
        where = []
        if types:
            types = [_type.value for _type in types]
            where.append(('in', 'club_type', types))
        if active_only:
            where.append(('=', 'club_inactive', False))

        pager_fetch, pager_return = pager

        tempdata = pager_fetch(
            database.fetch_onecol,
            cls.table,
            cls.identifier,
            {
                'where': where,
            }
        )
        return pager_return([cls(item) for item in tempdata])

    def activities(self, types=(), dates=(True, True)):
        from oclubs.objs import Activity

        return Activity.get_activities_conditions(
            types,
            {
                'where': [('=', 'act_club', self.id)],
            },
            dates=dates,
            order_by_time=True
        )

    @paged_db_read
    def allactphotos(self, pager=None):
        from oclubs.objs import Upload

        pager_fetch, pager_return = pager
        tempdata = pager_fetch(
            database.fetch_onecol,
            'act_pic',
            'actpic_upload',
            {
                'join': [('inner', 'activity', [('actpic_act', 'act_id')])],
                'where': [('=', 'act_club', self.id)],
            }
        )

        return pager_return([Upload(item) for item in tempdata])

    def add_member(self, user):
        database.insert_row('club_member',
                            {'cm_club': self.id, 'cm_user': user.id})
        del self.members

    def remove_member(self, user):
        database.delete_rows('club_member',
                             {'cm_club': self.id, 'cm_user': user.id})
        del self.members

    def send_invitation(self, user):
        from oclubs.objs.activity import date_int
        from oclubs.exceptions import AlreadyExists

        try:
            database.insert_row(
                'invitation',
                {'invitation_club': self.id,
                 'invitation_user': user.id,
                 'invitation_date': date_int(date.today())}
            )
        except AlreadyExists:
            pass

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
