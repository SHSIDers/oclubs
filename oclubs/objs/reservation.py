#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals, division

from datetime import date, timedelta

from oclubs.utils.dates import dateobj_to_int, int_to_dateobj, ONE_DAY
from oclubs.access import database
from oclubs.objs.base import BaseObject, Property, paged_db_read
from oclubs.enums import Building, ActivityTime, SBAppStatus, ResStatus


class Reservation(BaseObject):
    table = 'reservation'
    identifier = 'res_id'
    activity = Property('res_activity', 'Activity')  # for club reservations
    # the date for when the reservation is effective
    date = Property('res_date', (int_to_dateobj, dateobj_to_int))
    # the date for when the reservation was created
    date_of_reservation = Property('res_date_of_res',
                                   (int_to_dateobj, dateobj_to_int))
    timeslot = Property('res_timeslot', ActivityTime)
    status = Property('res_status', ResStatus)
    activity_name = Property('res_activity_name')
    reserver_name = Property('res_reserver_name')   # club name, teacher name
    reserver_club = Property('res_reserver_club', 'Club')
    owner = Property('res_owner', 'User')  # user that created the reservation
    classroom = Property('res_classroom', 'Classroom')
    SBNeeded = Property('res_SBNeeded', bool)
    SBAppDesc = Property('res_SBAppDesc')
    instructors_approval = Property('res_instructors_approval', bool)
    directors_approval = Property('res_directors_approval', bool)
    SBApp_status = Property('res_SBApp_status', SBAppStatus)

    @property
    def callsign(self):
        return '-'.join(filter(None, (
            str(self.id),
            self.classroom.location.replace(' ', '_'),
            str(dateobj_to_int(self.date))
        )))

    @classmethod
    @paged_db_read
    def get_reservations_conditions(cls, timeslot=None, additional_conds=None,
                                    dates=(True, True), status=None,
                                    room_buildings=(), reserver_club=None,
                                    room_numbers=(), SBNeeded=None,
                                    instructors_approval=None, owner=None,
                                    directors_approval=None,
                                    SBApp_status=None, order_by_date=True,
                                    pager=None):
        """
        Get reservations

        timeslot: ActivityTime object
        dates type: Date object
        room_building: either one Building object or list of Building objects
        room_number: list of strings

        return: list of Reservation objects
        """

        conds = {}
        if additional_conds:
            conds.update(additional_conds)

        conds['where'] = conds.get('where', [])

        if status is not None:
            conds['where'].append(('=', 'res_status', status.value))

        if SBNeeded is not None:
            conds['where'].append(('=', 'res_SBNeeded', SBNeeded))
        if instructors_approval is not None:
            conds['where'].append(('=', 'res_instructors_approval',
                                   instructors_approval))
        if directors_approval is not None:
            conds['where'].append(('=', 'res_directors_approval',
                                   directors_approval))
        if SBApp_status is not None:
            conds['where'].append(('=', 'res_SBApp_status',
                                   SBApp_status.value))

        if isinstance(dates, date):
            conds['where'].append(('=', 'res_date', dateobj_to_int(dates)))
        elif dates != (True, True):
            start, end = dates
            if start is True:
                conds['where'].append(('<=', 'res_date',
                                       dateobj_to_int(end or date.today())))
            elif end is True:
                conds['where'].append(('>=', 'res_date',
                                       dateobj_to_int(start or date.today())))
            else:
                start = (start or date.today()) + ONE_DAY
                end = (end or date.today()) + ONE_DAY
                conds['where'].append(('range', 'res_date',
                                       (dateobj_to_int(start),
                                        dateobj_to_int(end))))

        if timeslot:
            conds['where'].append(('=', 'res_timeslot', timeslot.value))

        if reserver_club:
            conds['where'].append(('=', 'res_reserver_club', reserver_club.id))

        if owner:
            conds['where'].append(('=', 'res_owner', owner))

        conds['join'] = conds.get('join', [])
        conds['join'].append(('inner', 'classroom',
                             [('room_id', 'res_classroom')]))

        if room_buildings:
            if isinstance(room_buildings, Building):
                conds['where'].append(('in', 'room_building',
                                       [room_buildings.value]))
            else:
                room_buildings = [room_building.value for
                                  room_building in room_buildings]
                conds['where'].append(('in', 'room_building', room_buildings))
        if room_numbers:
            conds['where'].append(('in', 'room_number', room_numbers))

        if order_by_date:
            conds['order'] = conds.get('order', [])
            conds['order'].append(('res_date', False))

        pager_fetch, pager_return = pager

        ret = pager_fetch(database.fetch_onecol,
                          cls.table,
                          cls.identifier,
                          conds, distinct=True)

        ret = [cls(item) for item in ret]

        return pager_return(ret)

    @classmethod
    def delete_reservation(cls, single_date=None, timeslot=None, building=None, room_number=None,
                           owner=None):
        conds = {}

        conds['where'] = conds.get('where', [])
        if single_date:
            conds['where'].append(('=', 'res_date', dateobj_to_int(single_date)))
        if timeslot:
            conds['where'].append(('=', 'res_timeslot', timeslot.value))
        if owner:
            conds['where'].append(('=', 'res_owner', owner.id))
        
        if building:
            conds['join'] = conds.get('join', [])
            conds['join'].append(('inner', 'classroom',
                                [('room_id', 'res_classroom')]))
        if building:
            conds['where'].append(('in', 'room_building',
                                [building.value]))
        if room_number:
            conds['where'].append(('in', 'room_number', [room_number]))

        ret = database.delete_rows(cls.table, conds)

        return ret
