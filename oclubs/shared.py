#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

import unicodecsv as csv
from io import BytesIO
import re

from flask import session, abort, request, make_response
from werkzeug.datastructures import Headers
from werkzeug.wrappers import Response

import oclubs
from oclubs.exceptions import NoRow


def get_club(club_info):
    '''From club_info get club object'''
    try:
        club_id = int(re.match(r'^\d+', club_info).group(0))
        club = oclubs.objs.Club(club_id)
    except (NameError, AttributeError, OverflowError, NoRow):
        abort(404)
    return club


def get_act(act_info):
    '''From act_info get activity object'''
    try:
        act_id = int(re.match(r'^\d+', act_info).group(0))
        act = oclubs.objs.Activity(act_id)
    except (NameError, AttributeError, OverflowError):
        abort(404)
    return act


def upload_picture(club_info):
    '''Handle upload object'''
    if 'user_id' not in session:
        abort(401)
    user_obj = oclubs.objs.User(session['user_id'])
    club_obj = get_club(club_info)
    file = request.files['picture']
    oclubs.objs.Upload.handle(user_obj, club_obj, file)


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
