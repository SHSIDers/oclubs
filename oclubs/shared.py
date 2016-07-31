#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from functools import wraps
from math import ceil
import re
from StringIO import StringIO
import xlsxwriter
from pyexcel_xlsx import get_data

from Crypto.Cipher import AES
from Crypto import Random

from flask import abort, request, g
from flask_login import current_user, login_required
from werkzeug.datastructures import Headers
from werkzeug.wrappers import Response

from oclubs.objs import Upload
from oclubs.access import get_secret
from oclubs.exceptions import NoRow
from oclubs.enums import UserType


class MemoryLine():
    def __init__(self):
        self.line_value = None

    def write(self, value):
        self.line_value = value


def _stringfy(string):
    if isinstance(string, unicode):
        return string.encode('utf-8')
    return string


def download_xlsx(filename, info):
    '''Çreate xlsx file for given info and download it '''
    output = StringIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()
    row_num = 0
    col_num = 0
    print info
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
    return Response(output.read(), mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers=headers)


def read_xlsx(file, data_type):
    '''Read xlsx and return a list of data'''
    raw = get_data(file)
    data = raw[data_type]
    if data_type == 'Users' and data[0] != ['Student ID', 'Passport Name', 'Email Address']:
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
                if current_user.id != club.teacher.id:
                    abort(403)
            else:
                if current_user.id != club.leader.id:
                    abort(403)
        return func(*args, **kwargs)

    return decorated_function


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

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num
