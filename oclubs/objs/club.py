#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

from datetime import date

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
    is_active = Property('club_inactive', lambda v: not v, search_require_true=True)
    intro = Property('club_intro', search=True)
    picture = Property('club_picture', 'Upload')
    type = Property('club_type', ClubType)
    joinmode = Property('club_joinmode', ClubJoinMode)
    reactivate = Property('club_reactivate', bool)
    reservation_allowed = Property('club_reservation_allowed', bool)
    smartboard_allowed = Property('club_smartboard_allowed', bool)
    smartboard_teacherapp_bypass = Property('club_smartboard_teacherapp_bypass', bool)
    smartboard_directorapp_bypass = Property('club_smartboard_directorapp_bypass', bool)
    members = ListProperty('club_member', 'cm_club', 'cm_user', 'User')
    all_act = ListProperty('activities', 'act_club', 'act_id', 'Activity')

    @property
    def teacher_and_members(self):
        ret = set(self.members)
        ret.add(self.teacher)
        return ret

    @property
    def is_excellent(self):
        return self in self.excellentclubs()

    @staticmethod
    def _excellentclubs():
        return redis.RedisList('excellentclubs', -1)

    # We can't use @property because fails with Club.excellentclubs = []
    # @deprecated
    @classmethod
    def excellentclubs(cls, amount=None):
        ret = cls.allclubs(excellent_only=True,
                           random_order=bool(amount), limit=amount)
        if amount:
            return ret[1]
        else:
            return ret

    @classmethod
    def set_excellentclubs(cls, newval):
        newval = [item.id for item in newval]
        lst = cls._excellentclubs()
        lst[:] = newval

    # @deprecated
    @classmethod
    def randomclubs(cls, amount, *args, **kwargs):
        ret = cls.allclubs(random_order=True, limit=amount,
                           *args, **kwargs)
        try:
            return ret[1]
        except IndexError:
            return ret

    @classmethod
    @paged_db_read
    def allclubs(cls, club_types=None, excellent_only=False, grade_limit=(),
                 active_only=True, additional_conds=(), random_order=False,
                 pager=None):
        conds = {}
        if additional_conds:
            conds.update(additional_conds)

        conds['where'] = conds.get('where', [])

        if club_types:
            types = [club_type.value for club_type in club_types]
            conds['where'].append(('in', 'club_type', types))
        if excellent_only:
            conds['where'].append(('in', 'club_id', cls._excellentclubs()))
        if grade_limit:
            conds['join'] = conds.get('join', [])
            conds['join'].append(
                ('inner', 'user', [('user_id', 'club_leader')]))
            conds['where'].append(('in', 'user_grade', grade_limit))
        if active_only:
            conds['where'].append(('=', 'club_inactive', False))
            conds['where'].append(('=', 'club_reactivate', True))
        if random_order:
            conds['order'] = conds.get('order', [])
            conds['order'].append((database.RawSQL('RAND()'), True))

        pager_fetch, pager_return = pager

        tempdata = pager_fetch(
            database.fetch_onecol,
            cls.table,
            cls.identifier,
            conds
        )
        return pager_return([cls(item) for item in tempdata])

    def activities(self, times=(), dates=(True, True), **kwargs):
        from oclubs.objs import Activity

        return Activity.get_activities_conditions(
            times,
            {
                'where': [('=', 'act_club', self.id)],
            },
            dates=dates,
            order_by_time=True,
            **kwargs
        )

    @paged_db_read
    def allactphotos(self, pager=None):
        from oclubs.objs import Activity, Upload

        pager_fetch, pager_return = pager
        tempdata = pager_fetch(
            database.fetch_multirow,
            'act_pic',
            {
                'actpic_upload': 'upload',
                'act_id': 'activity',
            },
            {
                'join': [('inner', 'activity', [('actpic_act', 'act_id')])],
                'where': [('=', 'act_club', self.id)],
            }
        )

        for item in tempdata:
            item['upload'] = Upload(item['upload'])
            item['activity'] = Activity(item['activity'])

        return pager_return(tempdata)

    def add_member(self, user):
        database.insert_row('club_member',
                            {'cm_club': self.id, 'cm_user': user.id})
        user.delete_invitation(self)
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
