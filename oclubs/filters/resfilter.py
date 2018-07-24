#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from flask import abort
from werkzeug.routing import PathConverter

from oclubs.enums import Building, ActivityTime


class ResFilter(object):
    DEFAULT = (None, None, None, None, None, None)
    # /[building]/[activity time]/[room numbers]/[SBNeeded]/[InstructorsApp]
    # /[DirectorsApp]

    def __init__(self, conds=None):
        self.conds = self.DEFAULT if conds is None else conds

    @classmethod
    def is_conds_admin(cls, conds):
        if len(conds) == 6:
            return True
        elif len(conds) == 3:
            return False
        else:
            abort(400)

    @classmethod
    def from_url(cls, url):
        room_building, activity_time, room_numbers, SBNeeded, \
            instructors_approval, directors_approval = cls.DEFAULT

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
                    activity_time = ActivityTime[conds[1].upper()]
                except KeyError:
                    pass

            if conds[2] != 'all':
                room_numbers = conds[2].split('-')

            if is_admin:
                if conds[3] != 'all':
                    SBNeeded = conds[3]
                if conds[4] != 'all':
                    instructors_approval = conds[4]
                if conds[5] != 'all':
                    directors_approval = conds[5]

        return cls((room_building,
                    activity_time,
                    room_numbers,
                    SBNeeded,
                    instructors_approval,
                    directors_approval))

    def to_url(self):
        return self.build_url(self.conds,
                              True
                              if self.is_conds_admin(self.conds) else False)

    def to_kwargs(self):
        ret = {}
        room_building, activity_time, room_numbers, SBNeeded, \
            instructors_approval, directors_approval = self.conds

        if room_building:
            ret['room_buildings'] = [room_building]
        if activity_time:
            ret['times'] = [activity_time]
        if room_numbers:
            ret['room_numbers'] = room_numbers
        if SBNeeded is not None:
            ret['SBNeeded'] = SBNeeded
        if instructors_approval is not None:
            ret['instructors_approval'] = instructors_approval
        if directors_approval is not None:
            ret['directors_approval'] = directors_approval

        return ret

    @classmethod
    def build_url(cls, conds, is_admin):
        if conds == cls.DEFAULT:
            return 'all'

        room_building, activity_time, room_numbers, SBNeeded, \
            instructors_approval, directors_approval = conds

        if room_numbers:
            room_numbers = [room_number.upper()
                            for room_number in room_numbers]
            newnumbers = '-'.join(room_numbers)

        if is_admin:
            return '/'.join(filter(None, (
                room_building.name.lower() if room_building else 'all',
                activity_time.name.lower() if activity_time else 'all',
                newnumbers if room_numbers else 'all',
                SBNeeded if SBNeeded is not None else 'all',
                instructors_approval
                if instructors_approval is not None
                else 'all',
                directors_approval
                if directors_approval is not None
                else 'all'
            )))
        else:
            return '/'.join(filter(None, (
                room_building.name.lower() if room_building else 'all',
                activity_time.name.lower() if activity_time else 'all',
                newnumbers if room_numbers else 'all',
            )))

    def toggle_url(self, identifier, cond, is_admin):
        room_building, activity_time, room_numbers, SBNeeded, \
            instructors_approval, directors_approval = self.conds

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

        if identifier == 'activity_time':
            if cond == 'all':
                activity_time = None
            else:
                try:
                    newtime = ActivityTime[cond.upper()]
                except KeyError:
                    pass
                else:
                    activity_time = newtime \
                        if newtime != activity_time else None

        if identifier == 'SBNeeded':
            SBNeeded = cond if cond != SBNeeded else None

        if identifier == 'instructors_approval':
            instructors_approval = cond \
                if cond != instructors_approval else None

        if identifier == 'directors_approval':
            directors_approval = cond if cond != directors_approval else None

        return self.build_url((room_building,
                               activity_time,
                               room_numbers,
                               SBNeeded,
                               instructors_approval,
                               directors_approval),
                              is_admin)

    def enumerate(self):
        return [
            {
                'name': 'Building',
                'identifier': 'room_building',
                'elements': [
                    {'url': 'XMT', 'name': 'XMT',
                     'selected': self.conds[0] ==
                        Building.XMT},
                    {'url': 'all', 'name': 'All buildings',
                     'selected': not self.conds[0]}
                ]
            },
            {
                'name': 'Timeslot',
                'identifier': 'activity_time',
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
                    {'url': 'true', 'name': 'Needed',
                     'selected': self.conds[3] is not None and True},
                    {'url': 'false', 'name': 'Not needed',
                     'selected': self.conds[3] is not None and False},
                    {'url': 'all', 'name': 'Both',
                     'selected': self.conds[3] is None},
                ]
            },
            {
                'name': 'Instructor',
                'identifier': 'instructors_approval',
                'elements': [
                    {'url': 'true', 'name': 'Approved',
                     'selected': self.conds[4] is not None and True},
                    {'url': 'false', 'name': 'Not approved',
                     'selected': self.conds[4] is not None and False},
                    {'url': 'all', 'name': 'Both',
                     'selected': self.conds[4] is None},
                ]
            },
            {
                'name': 'Director',
                'identifier': 'directors_approval',
                'elements': [
                    {'url': 'true', 'name': 'Approved',
                     'selected': self.conds[5] is not None and True},
                    {'url': 'false', 'name': 'Not approved',
                     'selected': self.conds[5] is not None and False},
                    {'url': 'all', 'name': 'Both',
                     'selected': self.conds[5] is None},
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
        if self.conds == self.DEFAULT:
            return 'All'
        else:
            room_building, activity_time, room_numbers, SBNeeded, \
                instructors_approval, directors_approval = self.conds

            return ' '.join(filter(None,
                                   (room_building.format_name
                                    if room_building else None,
                                    activity_time.format_name
                                    if activity_time else None,
                                    'for Select Classrooms'
                                    if room_numbers else None)))


class ResFilterConverter(PathConverter):
    def to_python(self, value):
        return ResFilter.from_url(value)

    def to_url(self, value):
        try:
            return value.to_url()
        except AttributeError:
            return value
