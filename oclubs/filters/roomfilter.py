#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from datetime import date

from flask import abort
from werkzeug.routing import PathConverter

from oclubs.utils.dates import (
    str_to_date_dict, date_to_str_dict, str_to_words_dict, int_to_dateobj,
    dateobj_to_int, this_week
)
from oclubs.enums import Building, ActivityTime


# current implementation, roomfilter supports only 1 building
# get_classroom_conditions and get_reservations_conditions support multiple
class RoomFilter(object):
    DEFAULT = (None, None, this_week())
    # url format: /all, gives defailt values
    # url format: /[building]/[timeslot]/[dates]
    # dates support thisweek, nextweek, today, tmrw, single date
    # or closed date range separate by - (both sides inclusive) [start, end]

    def __init__(self, conds=None):
        self.conds = self.DEFAULT if conds is None else conds

    @classmethod
    def is_url_valid(cls, conds):
        if len(conds) == 3:
            pass
        else:
            abort(404)

    # converts from str in urls to appropriate date object, single or range
    @classmethod
    def str_to_dates(cls, str):
        try:
            # see if str matches one of the date keywords
            dates = str_to_date_dict()[str]
            return dates
        except KeyError:
            dates = str.split('-')
            if len(dates) == 1:
                try:
                    return int_to_dateobj(dates[0])
                except ValueError:
                    abort(404)
            elif len(dates) == 2:
                try:
                    start = int_to_dateobj(dates[0])
                    end = int_to_dateobj(dates[1])
                except ValueError:
                    abort(404)
                else:
                    if start >= end:
                        abort(404)
                    else:
                        return (start, end)

    # converts from date object, single or range, to appropriate str for urls
    @classmethod
    def dates_to_str(cls, dates):
        if dates is None:
            return 'all'
        try:
            # see if dates matches one of the special dates/dateranges
            ret = date_to_str_dict()[dates]
            return ret
        except KeyError:
            if isinstance(dates, date):
                return str(dateobj_to_int(dates))
            else:
                ret = [str(dateobj_to_int(single_date)) for single_date in dates]
                return '-'.join(ret)

    @classmethod
    def from_url(cls, url):
        building, timeslot, dates = cls.DEFAULT

        if url and url != 'all':
            conds = url.split('/')

            cls.is_url_valid(conds)

            if conds[0] != 'all':
                try:
                    building = Building[conds[0].upper()]
                except KeyError:
                    pass

            if conds[1] != 'all':
                try:
                    timeslot = ActivityTime[conds[1].upper()]
                except KeyError:
                    pass

            if conds[2] != 'all':
                dates = cls.str_to_dates(conds[2].lower())

        return cls((building,
                    timeslot,
                    dates))

    def to_url(self):
        return self.build_url(self.conds)

    def to_kwargs(self):
        ret = {}
        building, timeslot, dates = self.conds

        if building:
            ret['buildings'] = [building]
        if timeslot:
            ret['timeslot'] = timeslot
        if dates:
            ret['dates'] = dates

        return ret

    @classmethod
    def build_url(cls, conds):
        # if conds == cls.DEFAULT:
        #     return 'all'

        building, timeslot, dates = conds

        return '/'.join(filter(None, (
            building.name.lower() if building else 'all',
            timeslot.name.lower() if timeslot else 'all',
            cls.dates_to_str(dates) if dates else 'all'
        )))

    def toggle_url(self, identifier, cond):
        building, timeslot, dates = self.conds

        if identifier == 'building':
            if cond == 'all':
                building = None
            else:
                try:
                    newbuilding = Building[cond.upper()]
                except KeyError:
                    pass
                else:
                    building = newbuilding if newbuilding != building else None

        if identifier == 'timeslot':
            if cond == 'all':
                timeslot = None
            else:
                try:
                    newtime = ActivityTime[cond.upper()]
                except KeyError:
                    pass
                else:
                    timeslot = newtime if newtime != timeslot else None

        return self.build_url((building, timeslot, dates))

    def enumerate(self):
        return [
            {
                'name': 'Building',
                'identifier': 'building',
                'elements': [
                    {'url': 'XMT', 'name': 'XMT',
                     'selected': self.conds[0] == Building.XMT},
                    {'url': 'ZTB', 'name': 'ZTB',
                     'selected': self.conds[0] == Building.ZTB},
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

    def enumerate_desktop(self):
        ret = self.enumerate()

        for group in ret:
            for elmt in group['elements']:
                elmt['url'] = self.toggle_url(group['identifier'],
                                              elmt['url'])

        return ret

    def enuermate_mobile(self):
        return self.enumerate_desktop()

    def title(self):
        building, timeslot, dates = self.conds

        if dates is None:
            date_str = None
        else:
            try:
                date_str = date_to_str_dict()[dates]
                date_str = str_to_words_dict()[date_str]
                date_str = 'for ' + date_str.title()
            except KeyError:
                if isinstance(dates, date):
                    date_str = 'for Selected Date'
                else:
                    date_str = 'for Selected Dates'

        return ' '.join(filter(None,
                               (building.format_name
                                if building else None,
                                timeslot.format_name
                                if timeslot else None,
                                date_str)))


class RoomFilterConverter(PathConverter):
    def to_python(self, value):
        return RoomFilter.from_url(value)

    def to_url(self, value):
        try:
                return value.to_url()
        except AttributeError:
                return value
