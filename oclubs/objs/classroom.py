#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals, division

from datetime import date

from oclubs.utils.dates import date_range_iterator
from oclubs.access import database
from oclubs.objs.base import BaseObject, Property, paged_db_read
from oclubs.objs.reservation import Reservation
from oclubs.enums import Building, ActivityTime


class Classroom(BaseObject):
    table = 'classroom'
    identifier = 'room_id'
    room_number = Property('room_number')
    studentsToUseLunch = Property('room_studentsToUseLunch', bool)
    studentsToUseAfternoon = Property('room_studentsToUseAfternoon', bool)
    building = Property('room_building', Building)
    desc = Property('room_desc')

    @property
    def location(self):
        ret = self.building.format_name + ' ' + self.room_number.upper()
        return ret

    @classmethod
    @paged_db_read
    def get_classroom_conditions(cls, additional_conds=None, buildings=(),
                                 timeslot=None, order_by_room_number=True,
                                 pager=None):

        """
        Get classrooms （regardless of whether it is reserved)

        buildings type: either one Building object or list of Building objects
        timeslot type: ActivityTime object

        :returns: Classroom objects
        :rtype: list
        """

        conds = {}
        if additional_conds:
            conds.update(additional_conds)

        conds['where'] = conds.get('where', [])

        if buildings:
            if isinstance(buildings, Building):
                conds['where']. \
                    append(('=', 'room_building', buildings.value))
            else:
                buildings = [building.value for building in buildings]
                conds['where'].append(('=', 'room_building', buildings))

        if timeslot:
            if timeslot == ActivityTime.AFTERSCHOOL:
                conds['where'].append(('=',
                                      'room_studentsToUseAfternoon', '1'))
            if timeslot == ActivityTime.NOON:
                conds['where'].append(('=', 'room_studentsToUseLunch', '1'))

        if order_by_room_number:
            conds['order'] = conds.get('order', [])
            conds['order'].append(('room_number', True))

        pager_fetch, pager_return = pager

        ret = pager_fetch(database.fetch_onecol,
                          cls.table,
                          cls.identifier,
                          conds)

        ret = [cls(item) for item in ret]

        return pager_return(ret)

    @classmethod
    def get_free_classroom_conditions(cls, buildings=(), timeslot=None,
                                      dates=(True, True)):

        '''
        Obtains free classrooms

        building, timeslot: enum objects
        dates: date object

        if date is provided: return structure
        ret = {
            building: {
                timeslot: {
                    date: rooms,
                    date: rooms,
                    ...
                },
                ...
            },
            ...
        }

        if date is not provided: return structure
        ret = {
            building: {
                timeslot: rooms,
                ...
            },
            ...
        }
        where building, timeslot, date are objects
        rooms are lists of classroom objects
        '''

        ret = {}

        # set up the buildings in ret
        if buildings:
            if isinstance(buildings, Building):
                ret[buildings] = {}
            else:
                for building in buildings:
                    ret[building] = {}
        else:
            # if unspecified then all buildings are included
            for building in Building:
                ret[building] = {}

        # each building
        for building in ret.keys():
            # set up timeslots in each ret[building]
            if timeslot:
                ret[building][timeslot] = {}
            else:
                # both timeslots are included if timeslot is None
                ret[building][ActivityTime.NOON] = {}
                ret[building][ActivityTime.AFTERSCHOOL] = {}

            # each timeslot for each building
            for timeslot in ret[building].keys():
                all_classrooms = cls.get_classroom_conditions(
                    buildings=building,
                    timeslot=timeslot)

                # no date is provided
                if dates == (True, True):
                    ret[building][timeslot] = all_classrooms
                # if date is provided
                else:
                    # set up dates in each ret[building][timeslot]
                    if isinstance(dates, date):
                        ret[building][timeslot][dates] = []
                    else:
                        start_date, end_date = dates
                        for single_date in date_range_iterator(start_date,
                                                               end_date):
                            ret[building][timeslot][single_date] = []

                    # each date for each timeslot for each building
                    for single_date in ret[building][timeslot].keys():
                        reservations = Reservation.get_reservations_conditions(
                            dates=single_date,
                            room_buildings=building,
                            timeslot=timeslot)

                        # free classroom = all classroom - reserved classroom
                        free_classrooms = list(all_classrooms)
                        for reservation in reservations:
                            try:
                                free_classrooms.remove(reservation.classroom)
                            except ValueError:
                                pass

                        ret[building][timeslot][single_date] = free_classrooms

        return ret
