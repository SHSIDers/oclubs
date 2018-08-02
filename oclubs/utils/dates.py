#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from datetime import datetime, date, timedelta

ONE_DAY = timedelta(days=1)

DATE_RANGE_MIN = date(2018, 8, 25)
DATE_RANGE_MAX = date(2019, 7, 5)


def today():
    return date.today()


def weekday():
    return date.today().weekday()


def tommorow():
    return today() + ONE_DAY


def this_week():
    return (today() - timedelta(weekday()),
            today() + timedelta(6 - weekday()))


def next_week():
    return (today() - timedelta(weekday()) + timedelta(7),
            today() + timedelta(6 - weekday()) + timedelta(7))


def next_next_week():
    return (today() - timedelta(weekday()) + timedelta(14),
            today() + timedelta(6 - weekday()) + timedelta(14))


def str_to_date_dict():
    return {'today': today(),
            'tmrw': tommorow(),
            'thisweek': this_week(),
            'nextweek': next_week(),
            'nextnextweek': next_next_week()}


def date_to_str_dict():
    return {d: s for s, d in str_to_date_dict().items()}


def str_to_words_dict():
    return {'today': 'today',
            'tmrw': 'tommorow',
            'thisweek': 'this week',
            'nextweek': 'next week',
            'nextnextweek': 'next next week'}


date_fmtstr = '%Y%m%d'


def int_to_dateobj(dateint):
    return datetime.strptime(str(dateint), date_fmtstr).date()


def dateobj_to_int(dateobj):
    return int(dateobj.strftime(date_fmtstr))


def date_range_iterator(start_date, end_date):
    # both sides inclusive: [start, end]
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)
