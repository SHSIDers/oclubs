#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from ConfigParser import ConfigParser
from functools import wraps
from math import ceil
import re
import unicodecsv

from Crypto.Cipher import AES
from Crypto import Random

from flask import session, abort, request, make_response, g
from flask_login import current_user, login_required
from werkzeug.datastructures import Headers
from werkzeug.wrappers import Response

import oclubs
from oclubs.exceptions import NoRow
from oclubs.enums import UserType


@login_required
def upload_picture(club):
    '''Handle upload object'''
    if request.files['picture'] == '':
        return
    file = request.files['picture']
    oclubs.objs.Upload.handle(current_user, club, file)


class MemoryLine():
    def __init__(self):
        self.line_value = None

    def write(self, value):
        self.line_value = value


def download_csv(filename, header, info):
    '''Create csv file for given info and download it'''
    # header as list, info as list of list
    def generate():
        m = MemoryLine()
        w = unicodecsv.writer(m, encoding='GB2312')
        w.writerow(header)
        yield m.line_value
        for row in info:
            w.writerow(row)
            yield m.line_value
    headers = Headers()
    headers.set('Content-Disposition', 'attachment', filename=filename)
    return Response(generate(), mimetype='text/csv', headers=headers)


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


def get_secret(name):
    config = ConfigParser()
    config.read('/srv/oclubs/secrets.ini')
    return config.get('secrets', name)


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
