#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

import os
from functools import wraps
from math import ceil
from pyexcel_xlsx import get_data
import re
from StringIO import StringIO
import xlsxwriter
from uuid import uuid4

from Crypto.Cipher import AES
from Crypto import Random

from flask import abort, g, flash, request, url_for, session
from flask_login import current_user, login_required
from werkzeug.datastructures import Headers
from werkzeug.wrappers import Response
from werkzeug.routing import PathConverter

import pystache

from oclubs.access.secrets import get_secret
from oclubs.exceptions import NoRow
from oclubs.objs.classroom import Classroom
from oclubs.enums import UserType, ClubType, ActivityTime, Building

with open('/srv/oclubs/oclubs/example.md', 'r') as f:
    markdownexample = f.read().strip()


def download_xlsx(filename, info):
    '''Çreate xlsx file for given info and download it '''
    output = StringIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()
    row_num = 0
    col_num = 0

    for row in info:
        for grid in row:
            worksheet.write(row_num, col_num, grid)
            col_num += 1
        col_num = 0
        row_num += 1
    workbook.close()
    output.seek(0)
    headers = Headers()
    headers.set('Content-Disposition', 'attachment', filename=filename)
    return Response(output.read(), mimetype='application/vnd.openxmlformats-'
                    'officedocument.spreadsheetml.sheet', headers=headers)


def read_xlsx(file, data_type, header):
    '''Read xlsx and return a list of data'''
    raw = get_data(file)
    data = raw[data_type]
    if [d.lower().strip().replace(' ', '') for d in data[0]] != header:
        raise ValueError
    contents = data[1:]
    return contents


def get_callsign(objtype, kw):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            try:
                item = int(re.match(r'^\d+', kwargs[kw]).group(0))
                item = objtype(item)
                item._data
            except (NameError, AttributeError, OverflowError, NoRow):
                abort(404)
            kwargs[kw] = item
            setattr(g, kw, item)
            return func(*args, **kwargs)

        return decorated_function

    return decorator


def special_access_required(func):
    @login_required
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.type != UserType.ADMIN:
            if 'club' in kwargs:
                club = kwargs['club']
            elif 'activity' in kwargs:
                club = kwargs['activity'].club
            else:
                abort(403)  # Admin-only page

            if current_user.type == UserType.TEACHER:
                if current_user != club.teacher:
                    abort(403)
            else:
                if current_user != club.leader:
                    abort(403)
        return func(*args, **kwargs)

    return decorated_function


def require_student_membership(func):
    @login_required
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'club' in kwargs:
            club = kwargs['club']
        elif 'activity' in kwargs:
            club = kwargs['activity'].club
        else:
            assert False

        if current_user not in club.members:
            abort(403)

        return func(*args, **kwargs)

    return decorated_function


def require_membership(func):
    @login_required
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.type != UserType.ADMIN:
            if 'club' in kwargs:
                club = kwargs['club']
            elif 'activity' in kwargs:
                club = kwargs['activity'].club
            else:
                assert False

            if current_user not in [club.teacher] + club.members:
                abort(403)

        return func(*args, **kwargs)

    return decorated_function


def require_not_student(func):
    @login_required
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.type == UserType.STUDENT:
            abort(403)

        return func(*args, **kwargs)

    return decorated_function


def require_active_club(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'club' in kwargs:
            club = kwargs['club']
        elif 'activity' in kwargs:
            club = kwargs['activity'].club
        else:
            assert False

        if not club.is_active:
            abort(403)

        return func(*args, **kwargs)

    return decorated_function


def require_past_activity(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        activity = kwargs['activity']

        if activity.is_future:
            abort(403)

        return func(*args, **kwargs)

    return decorated_function


def require_future_activity(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        activity = kwargs['activity']

        if not activity.is_future:
            abort(403)

        return func(*args, **kwargs)

    return decorated_function


def fail(msg, group):
    flash(msg, group)
    g.hasfailures = True


def true_or_fail(cond, msg, group):
    if not cond:
        fail(msg, group)


def error_or_fail(cond, exc, msg, group):
    try:
        cond()
    except exc:
        pass
    else:
        fail(msg, group)


def pass_or_fail(cond, exc, msg, group):
    try:
        cond()
    except exc:
        fail(msg, group)


def form_is_valid():
    return not g.get('hasfailures', False)


def _strify(st):
    if isinstance(st, unicode):
        return st.encode('utf-8')
    return str(st)


def encrypt(msg):
    key = get_secret('encrypt_key').decode('hex')
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CFB, iv)
    return (iv + cipher.encrypt(_strify(msg))).encode('base-64').strip()


def decrypt(msg):
    key = get_secret('encrypt_key').decode('hex')
    msg = msg.strip().decode('base-64')
    iv = msg[:16]
    cipher = AES.new(key, AES.MODE_CFB, iv)
    return cipher.decrypt(msg)[16:]


class Pagination(object):
    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=3,
                   right_current=4, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield {'num': None}
                if num == 1 or num == self.pages or abs(self.page - num) < 2:
                    yield {'num': num, 'hide': 0}  # Do not hide in phone
                elif abs(self.page - num) < 3:
                    yield {'num': num, 'hide': 1}  # Hide in phone secondly
                else:
                    yield {'num': num, 'hide': 2}  # Hide in phone firstly
                last = num


def render_email_template(name, parameters):
    with open(os.path.join('/srv/oclubs/oclubs/email_templates/',
                           name + '.mustache'), 'r') as textfile:
        data = textfile.read()

    return pystache.render(data, parameters)


def partition(p, l):
    return reduce(lambda x, y: x[not p(y)].append(y) or x, l, ([], []))


class ClubFilter(object):
    DEFAULT = (False, None, None)
    GRADE_REGEX = re.compile(r'([01]?[0-9])-([01]?[0-9])')

    def __init__(self, conds=None, is_single_club=False):
        self.conds = self.DEFAULT if conds is None else conds
        self.is_single_club = is_single_club

    @classmethod
    def from_url(cls, url):
        excellent, typ, grade = cls.DEFAULT
        if url and url != 'all':
            for cond in url.split('/'):
                if cond == 'excellent':
                    excellent = True
                else:
                    try:
                        typ = ClubType[cond.upper()]
                        continue
                    except KeyError:
                        pass

                    reobj = cls.GRADE_REGEX.match(cond)
                    if reobj:
                        grade = range(int(reobj.group(1)),
                                      int(reobj.group(2)) + 1)
                        continue

                        abort(404)

        return cls((excellent, typ, grade))

    @classmethod
    def from_club(cls, club):
        grade = [0, 1] if club.leader.grade % 2 else [-1, 0]
        grade = map(lambda x: x + club.leader.grade, grade)
        return cls((club.is_excellent, club.type, grade), is_single_club=True)

    def to_url(self):
        return self.build_url(self.conds)

    def to_kwargs(self):
        ret = {}
        excellent, typ, grade = self.conds
        if excellent:
            ret['excellent_only'] = True
        if typ:
            ret['club_types'] = [typ]
        if grade:
            ret['grade_limit'] = grade

        return ret

    @classmethod
    def build_url(cls, conds):
        if conds == cls.DEFAULT:
            return 'all'

        excellent, typ, grade = conds
        return '/'.join(filter(None, (
            'excellent' if excellent else None,
            typ.name.lower() if typ else None,
            '%d-%d' % (grade[0], grade[-1]) if grade else None
        )))

    def toggle_url(self, cond):
        excellent, typ, grade = self.conds
        if cond in ['all', 'excellent']:
            return self.build_url((['all', 'excellent'].index(cond),
                                   typ, grade))
        else:
            try:
                newtyp = ClubType[cond.upper()]
            except KeyError:
                pass
            else:
                return self.build_url((excellent,
                                      newtyp if newtyp != typ else None,
                                      grade))

            reobj = self.GRADE_REGEX.match(cond)
            newgrade = range(int(reobj.group(1)),
                             int(reobj.group(2)) + 1)
            return self.build_url((excellent, typ,
                                  newgrade if newgrade != grade else None))

    def enumerate(self):
        return [
            {
                'name': 'Achievement',
                'elements': [
                    {'url': 'all', 'name': 'All Clubs',
                     'selected': not self.conds[0]},
                    {'url': 'excellent', 'name': 'Excellent Clubs',
                     'selected': self.conds[0]}
                ]
            },
            {
                'name': 'Club Types',
                'elements': [
                    {'url': t.name.lower(), 'name': t.format_name,
                     'selected': self.conds[1] == t}
                    for t in ClubType
                ]
            },
            {
                'name': 'Grades',
                'elements': [
                    {'url': '9-10', 'name': 'Grade 9 - 10',
                     'selected': self.conds[2] == [9, 10]},
                    {'url': '11-12', 'name': 'Grade 11 - 12',
                     'selected': self.conds[2] == [11, 12]},
                ]
            },
        ]

    def enumerate_desktop(self):
        ret = self.enumerate()

        if not self.is_single_club:
            for group in ret:
                for elmt in group['elements']:
                    elmt['url'] = self.toggle_url(elmt['url'])

        return ret

    def enumerate_mobile(self):
        ret = []
        hasselection = False

        for group in self.enumerate():
            for elmt in group['elements']:
                if hasselection or elmt['url'] == 'all':
                    elmt['selected'] = False
                else:
                    hasselection = elmt['selected']

                ret.append(elmt)

        # all clubs
        ret[0]['selected'] = not hasselection

        return ret

    def title(self):
        excellent, typ, grade = self.conds
        return ' '.join(filter(None, (
            ['All Clubs', 'Excellent Clubs'][excellent],
            'of ' + typ.format_name if typ else None,
            'in Grade %d - %d' % (grade[0], grade[-1]) if grade else None
        )))


class ResFilter(object):
    DEFAULT = (None, None, None, None, None, None)
    # /[building]/[activity time]/[room numbers]/[SBNeeded]/[InstructorsApp]
    # /[DirectorsApp]

    def __init__(self, conds=None):
        self.conds = self.DEFAULT if conds is None else conds

    @classmethod
    def room_numbers_filter(cls, room_building, room_numbers):
        ret = ()
        r_numbers = Classroom.get_classroom_conditions(
            building=room_building)
        for room_number in room_numbers:
            if room_number in r_numbers:
                ret.extend(room_number)
        return ret

    @classmethod
    def from_url(cls, url):
        room_building, activity_time, room_numbers, SBNeeded, \
            instructors_approval, directors_approval = cls.DEFAULT

        if url and url != 'all':
            conds = url.split('/')

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
                room_numbers = cls.room_numbers_filter(room_building,
                                                       conds[2].split('%'))

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
        return self.build_url(self.conds)

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
    def build_url(cls, conds):
        if conds == cls.DEFAULT:
            return 'all'

        room_building, activity_time, room_numbers, SBNeeded, \
            instructors_approval, directors_approval = conds

        if room_numbers:
            newnumbers = '%'.join(cls.room_numbers_filter(room_building,
                                                          room_numbers))
            newnumbers = list(map(str.lower(), newnumbers))

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

    def toggle_url(self, identifier, cond):
        room_building, activity_time, room_numbers, SBNeeded, \
            instructors_approval, directors_approval = self.conds

        if identifier == 'room_building':
            try:
                newbuilding = Building[cond.upper()]
            except KeyError:
                pass
            else:
                return self.build_url((newbuilding
                                       if newbuilding != room_building
                                       else None,
                                       activity_time,
                                       room_numbers,
                                       SBNeeded,
                                       instructors_approval,
                                       directors_approval))

        if identifier == 'activity_time':
            try:
                newtime = ActivityTime[cond.upper()]
            except KeyError:
                pass
            else:
                return self.build_url((room_building,
                                       newtime
                                       if newtime != activity_time
                                       else None,
                                       room_numbers,
                                       SBNeeded,
                                       instructors_approval,
                                       directors_approval))

        if identifier == 'room_number':
            if cond:
                newnumbers = self.room_numbers_filter(cond)
                return self.build_url((room_building,
                                       activity_time,
                                       newnumbers,
                                       SBNeeded,
                                       instructors_approval,
                                       directors_approval))
            else:
                return self.build_url((room_building,
                                       activity_time,
                                       None,
                                       SBNeeded,
                                       instructors_approval,
                                       directors_approval))

        if identifier == 'SBNeeded':
            return self.build_url((room_building,
                                   activity_time,
                                   room_numbers,
                                   cond if cond != SBNeeded else None,
                                   instructors_approval,
                                   directors_approval))

        if identifier == 'instructors_approval':
            return self.build_url((room_building,
                                   activity_time,
                                   room_numbers,
                                   SBNeeded,
                                   cond
                                   if cond != instructors_approval
                                   else None,
                                   directors_approval))

        if identifier == 'directors_approval':
            return self.build_url((room_building,
                                   activity_time,
                                   room_numbers,
                                   SBNeeded,
                                   instructors_approval,
                                   cond
                                   if cond != directors_approval
                                   else None))

    def enumerate(self):
        return [
            {
                'name': 'Building',
                'identifier': 'room_building',
                'elements': [
                    {'url': 'xmt', 'name': 'XMT',
                     'selected': self.conds[0] == 1},
                    {'url': 'all', 'name': 'All buildings',
                     'selected': not self.conds[0]}
                ]
            },
            {
                'name': 'Timeslot',
                'identifier': 'activity_time',
                'elements': [
                    {'url': 'afterschool', 'name': 'Afterschool',
                     'selected': self.conds[1] ==
                        ActivityTime.AFTERSCHOOL.value},
                    {'url': 'noon', 'name': 'Lunch',
                     'selected': self.conds[1] ==
                        ActivityTime.NOON.value},
                    {'url': 'all', 'name': 'All timeslots',
                     'selected': not self.conds[1]}
                ]
            },
            # {
            #     'name': 'Classroom',
            #     'identifier': 'room_number',
            #     'elements': [
            #         {'url': n, 'name': n,
            #          'selected': n in self.conds[2]}
            #         for n in Classroom.get_classroom_conditions(
            #             building=self.conds[0]),
            #         {'url': 'all', 'name': 'All classrooms',
            #          'selected': self.conds[2] is None}
            #     ]
            # },
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
            },
        ]

    def enumerate_desktop(self):
        ret = self.enumerate()

        # for group in ret:
        #     for elmt in group['elements']:
        #         elmt['url'] = self.toggle_url(group['identifier'],
        #                                       elmt['url'])

        return ret

    def enumerate_mobile(self):
        ret = []

        return ret

    def title(self):
        return 'Unfinished'


# Setup stuffs
def get_picture(picture, ext='jpg'):
    return url_for('static', filename='images/' + picture + '.' + ext)


def url_for_other_page(page):
    args = request.view_args.copy()
    args.update(request.args)
    args['page'] = page
    return url_for(request.endpoint, **args)


def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = str(uuid4())
    return session['_csrf_token']


class ClubFilterConverter(PathConverter):
    def to_python(self, value):
        return ClubFilter.from_url(value)

    def to_url(self, value):
        try:
            return value.to_url()
        except AttributeError:
            return value


class ResFilterConverter(PathConverter):
    def to_python(self, value):
        return ResFilter.from_url(value)

    def to_url(self, value):
        try:
            return value.to_url()
        except AttributeError:
            return value


def init_app(app):
    app.jinja_env.globals['getpicture'] = get_picture
    app.jinja_env.globals['url_for_other_page'] = url_for_other_page
    app.jinja_env.globals['csrf_token'] = generate_csrf_token
    app.jinja_env.globals['ClubFilter'] = ClubFilter
    app.jinja_env.globals['ResFilter'] = ResFilter

    app.url_map.converters['clubfilter'] = ClubFilterConverter
    app.url_map.converters['resfilter'] = ResFilterConverter
