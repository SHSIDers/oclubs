#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals, division

from datetime import datetime, date, timedelta

from oclubs.access import database
from oclubs.enums import ActivityTime, Building
from oclubs.objs.base import BaseObject, Property, paged_db_read
from oclubs.objs.activity import Activity

ONE_DAY = timedelta(days=1)


def int_date(dateint):
    return datetime.strptime(str(dateint), Activity.date_fmtstr).date()


def date_int(dateobj):
    return int(dateobj.strftime(Activity.date_fmtstr))


class Reservation(BaseObject):
    table = 'reservation'
    identifier = 'res_id'
    activity = Property('res_activity', 'Activity')
    classroom = Property('res_classroom', 'Classroom')
    SBNeeded = Property('res_SBNeeded', bool)
    SBAppDesc = Property('res_SBAppDesc', bool)
    instructors_approval = Property('res_instructors_approval', bool)
    directors_approval = Property('res_directors_approval', bool)
    SBApp_success = Property('res_SBApp_success', bool)

    @property
    def classroomRoomNumber(self):
        ret = database.fetch_oneentry(self.table,
                                      'room_number',
                                      {'room_id': self.classroom.id})
        return ret.upper()

    @property
    def classroomBuilding(self):
        ret = database.fetch_oneentry(cls.table,
                                      'room_building',
                                      {'room_id': self.classroom.id})
        return ret.formatname()

    def update_SBApp_success(self):
        if self.instructors_approval and self.directors_approval:
            self.SBApp_success = True
            return True

        return False

    def update_instructors_approval(self, is_approved):
        self.instructors_approval = is_approved
        self.update_SBApp_success(self)

    def update_directors_approval(self, is_approved):
        self.directors_approval = is_approved
        self.update_SBApp_success(self)

    @classmethod
    @paged_db_read
    def get_reservations_conditions(cls, times=(), additional_conds=None,
                                    dates=(True, True), room_buildings=(),
                                    room_numbers=(), SBNeeded=None,
                                    instructors_approval=None,
                                    directors_approval=None,
                                    SBApp_success=None, order_by_time=True,
                                    pager=None):
        conds = {}
        if additional_conds:
            conds.update(additional_conds)

        conds['join'] = conds.get('join', [])
        conds['join'].append(('inner', 'activity',
                             [('act_id', 'res_activity')]))
        conds['where'] = conds.get('where', [])
        if isinstance(dates, date):
            conds['where'].append(('=', 'act_date', date_int(dates)))
        elif dates != (True, True):
            start, end = dates

            if start is True:
                conds['where'].append(('<=', 'act_date',
                                       date_int(end or date.today())))
            elif end is True:
                conds['where'].append(('>', 'act_date',
                                       date_int(start or date.today())))
            else:
                start = (start or date.today()) + ONE_DAY
                end = (end or date.today()) + ONE_DAY
                conds['where'].append(('range', 'act_date',
                                       (date_int(start), date_int(end))))

        if times:
            times = [time.value for time in times]
            conds['where'].append(('in', 'act_time', times))

        conds['join'] = conds.get('join', [])
        conds['join'].append(('inner', 'classroom',
                             [('room_id', 'res_classroom')]))
        if room_buildings:
            room_buildings = [room_building.value for
                              room_building in room_buildings]
            conds['where'].append(('in', 'room_building', room_buildings))
        if room_numbers:
            conds['where'].append(('in', 'room_number', room_numbers))

        if SBNeeded is not None:
            conds['where'].append(('=', 'res_SBNeeded', SBNeeded))
        if instructors_approval is not None:
            conds['where'].append(('=', 'res_instructors_approval',
                                   instructors_approval))
        if directors_approval is not None:
            conds['where'].append(('=', 'res_directors_approval',
                                   directors_approval))
        if SBApp_success is not None:
            conds['where'].append(('=', 'res_SBApp_success', SBApp_success))

        if order_by_time:
            conds['order'] = conds.get('order', [])
            conds['order'].append(('act_date', False))

        pager_fetch, pager_return = pager

        ret = pager_fetch(database.fetch_onecol, 'reservation', 'res_id',
                          conds, distinct=True)

        ret = [cls(item) for item in ret]

        return pager_return(ret)

    @classmethod
    def thisweek_reservations(cls):
        weekday = date.today().weekday()
        today = date.today()
        return cls.get_reservations_conditions(
            dates=(today - timedelta(weekday + 1),
                   today + timedelta(6 - weekday)))

    @classmethod
    def today_reservations(cls):
        today = date.today()
        return cls.get_reservations_conditions(dates=today)
