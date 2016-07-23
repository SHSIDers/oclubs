#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from functools import wraps
from io import BytesIO
import re
import unicodecsv as csv

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
    file = request.files['picture']
    oclubs.objs.Upload.handle(current_user, club, file)


def download_csv(filename, header, info):
    '''Create csv file for given info and download it'''
    # header as list, info as list of list
    def generate():
        yield ','.join(header) + '\n'
        for row in info:
            yield ','.join(row) + '\n'
    headers = Headers()
    headers.set('Content-Disposition', 'attachment', filename=filename)
    return Response(generate(), mimetype='text/csv', headers=headers)
    # f = BytesIO()
    # w = csv.writer(f, encoding='utf-16')
    # _ = w.writerow(header)
    # _ = f.seek(0)


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
        if 'club' in kwargs:
            club = kwargs['club']
        elif 'activity' in kwargs:
            club = kwargs['activity'].club
        else:
            abort(500)  # Assertion

        if current_user.type == UserType.ADMIN:
            return
        elif current_user.type == UserType.TEACHER:
            if current_user.id != club.teacher.id:
                abort(403)
        else:
            if current_user.id != club.leader.id:
                abort(403)
        return func(*args, **kwargs)

    return decorated_function
