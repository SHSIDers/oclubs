#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from flask import abort
from werkzeug.routing import PathConverter

from oclubs.enums import Building, ActivityTime, SBAppStatus


# current implementation, resfilter supports only 1 building
# get_classroom_conditions and get_reservations_conditions support multiple
class ResFilter(object):
    DEFAULT = (None, None, None, None, None)
    # url format: /all, gives default filter values
    # url format: /[building]/[timeslot]/[room numbers]/[SBNeeded]
    # /[SBApp_status]
    # room numbers separated by -
    # url /[SBNeeded]/[InstructorsApp]/[DirectorsApp] optional
    # if not provided, those will be default value

    def __init__(self, conds=None):
        self.conds = self.DEFAULT if conds is None else conds

    # also checks url format
    @classmethod
    def is_conds_admin(cls, conds):
        if len(conds) == 5:
            return True
        elif len(conds) == 3:
            return False
        else:
            abort(404)

    @classmethod
    def from_url(cls, url):
        room_building, timeslot, room_numbers, SBNeeded, \
            SBApp_status = cls.DEFAULT

        if url and url != 'all':
            conds = url.split('/')

            # placed here to catch incorrect url requests
            is_admin = cls.is_conds_admin(conds)

            if conds[0] != 'all':
                try:
                    room_building = Building[conds[0].upper()]
                except KeyError:
                    pass

            if conds[1] != 'all':
                try:
                    timeslot = ActivityTime[conds[1].upper()]
                except KeyError:
                    pass

            if conds[2] != 'all':
                room_numbers = conds[2].split('-')

            if is_admin:
                if conds[3] != 'all':
                    SBNeeded = True if conds[3] == 'true' else False

                if conds[4] != 'all':
                    try:
                        SBApp_status = SBAppStatus[conds[4].upper()]
                    except KeyError:
                        pass

        return cls((room_building,
                    timeslot,
                    room_numbers,
                    SBNeeded,
                    SBApp_status))

    def to_url(self):
        return self.build_url(self.conds, self.is_conds_admin(self.conds))

    def to_kwargs(self):
        ret = {}
        room_building, timeslot, room_numbers, SBNeeded, \
            SBApp_status = self.conds

        if room_building:
            ret['room_buildings'] = [room_building]
        if timeslot:
            ret['timeslot'] = timeslot
        if room_numbers:
            ret['room_numbers'] = room_numbers
        if SBNeeded is not None:
            ret['SBNeeded'] = SBNeeded
        if SBApp_status is not None:
            ret['SBApp_status'] = SBApp_status

        return ret

    @classmethod
    def build_url(cls, conds, is_admin):
        if conds == cls.DEFAULT:
            return 'all'

        room_building, timeslot, room_numbers, SBNeeded, \
            SBApp_status = conds

        if room_numbers:
            room_numbers = [room_number.upper()
                            for room_number in room_numbers]
            newnumbers = '-'.join(room_numbers)

        if SBNeeded is None:
            SBNeeded_str = 'all'
        else:
            SBNeeded_str = 'true' if SBNeeded else 'false'

        if is_admin:
            return '/'.join((
                room_building.name.lower() if room_building else 'all',
                timeslot.name.lower() if timeslot else 'all',
                newnumbers if room_numbers else 'all',
                SBNeeded_str,
                SBApp_status.name.lower() if SBApp_status else 'all'
            ))
        else:
            return '/'.join((
                room_building.name.lower() if room_building else 'all',
                timeslot.name.lower() if timeslot else 'all',
                newnumbers if room_numbers else 'all',
            ))

    def toggle_url(self, identifier, cond, is_admin):
        room_building, timeslot, room_numbers, SBNeeded, \
            SBApp_status = self.conds

        if identifier == 'room_building':
            if cond == 'all':
                room_building = None
            else:
                try:
                    newbuilding = Building[cond.upper()]
                except KeyError:
                    pass
                else:
                    room_building = newbuilding \
                        if newbuilding != room_building else None

        if identifier == 'timeslot':
            if cond == 'all':
                timeslot = None
            else:
                try:
                    newtime = ActivityTime[cond.upper()]
                except KeyError:
                    pass
                else:
                    timeslot = newtime \
                        if newtime != timeslot else None

        if identifier == 'SBNeeded':
            SBNeeded = cond if cond != SBNeeded else None

        if identifier == 'SBApp_status':
            if cond == 'all':
                SBApp_status = None
            else:
                try:
                    newstatus = SBAppStatus[cond.upper()]
                except KeyError:
                    pass
                else:
                    SBApp_status = newstatus \
                        if newstatus != SBApp_status else None

        return self.build_url((room_building,
                               timeslot,
                               room_numbers,
                               SBNeeded,
                               SBApp_status),
                              is_admin)

    def enumerate(self):
        return [
            {
                'name': 'Building',
                'identifier': 'room_building',
                'elements': [
                    {'url': 'XMT', 'name': 'XMT',
                     'selected': self.conds[0] == Building.XMT},
                    {'url': 'ZXB', 'name': 'ZXB',
                     'selected': self.conds[0] == Building.ZXB},
                    {'url': 'all', 'name': 'All buildings',
                     'selected': not self.conds[0]},
                ]
            },
            {
                'name': 'Timeslot',
                'identifier': 'timeslot',
                'elements': [
                    {'url': 'AFTERSCHOOL', 'name': 'Afterschool',
                     'selected': self.conds[1] ==
                        ActivityTime.AFTERSCHOOL},
                    {'url': 'NOON', 'name': 'Lunch',
                     'selected': self.conds[1] ==
                        ActivityTime.NOON},
                    {'url': 'all', 'name': 'All timeslots',
                     'selected': not self.conds[1]}
                ]
            }
        ]

    def enumerate_admin(self):
        return [
            {
                'name': 'Smartboard',
                'identifier': 'SBNeeded',
                'elements': [
                    {'url': True, 'name': 'Needed',
                     'selected': self.conds[3] is not None and self.conds[3]},
                    {'url': False, 'name': 'Not needed',
                     'selected': self.conds[3] is not None and
                        not self.conds[3]},
                    {'url': None, 'name': 'Both',
                     'selected': self.conds[3] is None},
                ]
            },
            {
                'name': 'Smartboard Application Status',
                'identifier': 'SBApp_status',
                'elements': [
                    {'url': 'pending', 'name': 'Pending',
                     'selected': self.conds[4] == SBAppStatus.PENDING},
                    {'url': 'approved', 'name': 'Approved',
                     'selected': self.conds[4] == SBAppStatus.APPROVED},
                    {'url': 'rejected', 'name': 'Rejected',
                     'selected': self.conds[4] == SBAppStatus.REJECTED},
                    {'url': 'na', 'name': 'N/A',
                     'selected': self.conds[4] == SBAppStatus.NA},
                    {'url': 'all', 'name': 'All',
                     'selected': self.conds[4] is None},
                ]
            }
        ]

    def enumerate_desktop(self, is_admin):
        ret = self.enumerate()

        if is_admin:
            ret += self.enumerate_admin()

        for group in ret:
            for elmt in group['elements']:
                elmt['url'] = self.toggle_url(group['identifier'],
                                              elmt['url'],
                                              is_admin)

        return ret

    def enumerate_mobile(self, is_admin):
        return self.enumerate_desktop(is_admin)

    def title(self):
        # only one building rn, so always show XMT
        if self.conds == self.DEFAULT:
            return 'XMT'
        else:
            room_building, timeslot, room_numbers, SBNeeded, \
                SBApp_status = self.conds

            if room_numbers is None:
                room_str = None
            elif len(room_numbers) == 1:
                room_str = 'for Selected Classroom'
            else:
                room_str = 'for Selected Classrooms'

            return ' '.join(filter(None,
                                   ('XMT',
                                    timeslot.format_name
                                    if timeslot else None,
                                    room_str)))


class ResFilterConverter(PathConverter):
    def to_python(self, value):
        return ResFilter.from_url(value)

    def to_url(self, value):
        try:
            return value.to_url()
        except AttributeError:
            return value
