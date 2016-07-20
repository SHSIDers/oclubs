#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

import csv
import re

from flask import session, abort, request, stream_with_context
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
    oclubs.objs.Upload.handle_upload(user_obj, club_obj, file)


def download_csv(filename, header, info):
    '''Create csv file for given info and download it'''
    # header as list, info as list of list
    def generate():
        w = csv.writer()

        w.writerow(filename)
        for row in info:
            w.writerow(row)
            # yield data.getvalue()
    headers = Headers()
    headers.set('Content-Disposition', 'attachment', filename=filename)
    return Response(
        stream_with_context(generate()),
        mimetype='text/csv', headers=headers
    )
