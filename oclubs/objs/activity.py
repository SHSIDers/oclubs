#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals, division

from datetime import datetime, date, timedelta
import json

from oclubs.access import database
from oclubs.enums import ActivityTime
from oclubs.objs.base import BaseObject, Property, ListProperty, paged_db_read

ONE_DAY = timedelta(days=1)


def int_date(dateint):
    return datetime.strptime(str(dateint), Activity.date_fmtstr).date()


def date_int(dateobj):
    return int(dateobj.strftime(Activity.date_fmtstr))


class Activity(BaseObject):
    table = 'activity'
    identifier = 'act_id'
    name = Property('act_name', search=True)
    club = Property('act_club', 'Club')
    description = Property('act_desc', 'FormattedText', search=True)
    date = Property('act_date', (int_date, date_int))
    time = Property('act_time', ActivityTime)
    location = Property('act_location')
    cas = Property('act_cas', (lambda val: val/60, lambda val: val*60))
    post = Property('act_post', 'FormattedText', search=True)
    selections = Property('act_selections', json, error_default='[]')
    reservation = Property('act_reservation', 'Reservation')
    attendance = ListProperty('attendance', 'att_act', 'att_user', 'User')
    pictures = ListProperty('act_pic', 'actpic_act', 'actpic_upload', 'Upload')

    date_fmtstr = '%Y%m%d'

    @property
    def is_future(self):
        return self.date > date.today()

    @property
    def one_line_selections(self):
        return ';'.join(self.selections)

    def signup(self, user, **kwargs):
        data = {
            'signup_consentform': ('consentform', False),
            'signup_selection': ('selection', '')
        }

        insert = {'signup_act': self.id, 'signup_user': user.id}
        update = {}

        for dbkey, (kwkey, default) in data.items():
            if kwkey in kwargs:
                insert[dbkey] = kwargs[kwkey]
                update[dbkey] = kwargs[kwkey]
            else:
                insert[dbkey] = default

        database.insert_or_update_row('signup', insert, update)

    def signup_undo(self, user):
        database.delete_rows(
            'signup',
            {'signup_act': self.id, 'signup_user': user.id}
        )

    def signup_list(self):
        from oclubs.objs import User

        ret = database.fetch_multirow(
            'signup',
            {
                'signup_user': 'user',
                'signup_consentform': 'consentform',
                'signup_selection': 'selection'
            },
            {'signup_act': self.id}
        )
        for item in ret:
            item['user'] = User(item['user'])

        return ret

    def signup_user_status(self, user):
        return database.fetch_onerow(
            'signup',
            {
                'signup_consentform': 'consentform',
                'signup_selection': 'selection'
            },
            {
                'signup_act': self.id,
                'signup_user': user.id
            }
        )

    def attend(self, user):
        database.insert_row(
            'attendance',
            {'att_act': self.id, 'att_user': user.id}
        )
        del self.attendance

    def attend_undo(self, user):
        database.delete_rows(
            'attendance',
            {'att_act': self.id, 'att_user': user.id}
        )
        del self.attendance

    def add_picture(self, upload):
        database.insert_row('act_pic',
                            {'actpic_act': self.id,
                             'actpic_upload': upload.id})
        del self.pictures

    def remove_picture(self, upload):
        database.delete_rows('act_pic',
                             {'actpic_act': self.id,
                              'actpic_upload': upload.id})
        del self.pictures

    @classmethod
    @paged_db_read
    def get_activities_conditions(cls, times=(), additional_conds=None,
                                  dates=(True, True), club_types=(),
                                  excellent_only=False, grade_limit=(),
                                  require_photos=False, require_attend=False,
                                  order_by_time=True, pager=None):
        conds = {}
        if additional_conds:
            conds.update(additional_conds)

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

        if club_types or excellent_only or grade_limit:
            conds['join'] = conds.get('join', [])
            conds['join'].append(('inner', 'club', [('club_id', 'act_club')]))
        if club_types:
            club_types = [club_type.value for club_type in club_types]
            conds['where'].append(('in', 'club_type', club_types))
        if excellent_only:
            from oclubs.objs import Club
            conds['where'].append(('in', 'club_id', Club._excellentclubs()))
        if grade_limit:
            conds['join'].append(
                ('inner', 'user', [('user_id', 'club_leader')]))
            conds['where'].append(('in', 'user_grade', grade_limit))

        if require_photos:
            conds['join'] = conds.get('join', [])
            conds['join'].append(
                ('inner', 'act_pic', [('actpic_act', 'act_id')]))
        if require_attend:
            conds['join'] = conds.get('join', [])
            conds['join'].append(
                ('inner', 'attendance', [('att_act', 'act_id')]))

        if order_by_time:
            conds['order'] = conds.get('order', [])
            conds['order'].append(('act_date', False))

        pager_fetch, pager_return = pager

        ret = pager_fetch(database.fetch_onecol,
                          cls.table,
                          cls.identifier,
                          conds,
                          distinct=True)

        ret = [cls(item) for item in ret]

        return pager_return(ret)

    @classmethod
    def all_activities(cls):
        return cls.get_activities_conditions()

    @classmethod
    def thisweek_activities(cls):
        weekday = date.today().weekday()
        today = date.today()
        return cls.get_activities_conditions(
            dates=(today - timedelta(weekday + 1),
                   today + timedelta(6 - weekday)))
