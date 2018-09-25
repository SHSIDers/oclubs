#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals, print_function
import sys

from flask import jsonify, request
from oclubs.objs import Club
from oclubs.shared import get_callsign as getobj
from oclubs.access import elasticsearch

'''DB fields'''
_esfields = ['club_name', 'club_desc', 'club_intro']


def mpserialize():
    action = request.args['action']
    data = {}
    if (action == 'getClubPreview'):
        cid = request.args['clubid']
        club = getobj(Club, cid)
        data = {
            'name': club.name,
            'imagesrc': club.picture.location_external
        }

    if (action == 'getClubDetail'):
        cid = request.args['clubid']
        club = getobj(Club, cid)

        images = [item['upload'].location_external
                  for item in club.allactphotos()]

        data = {
            'clubid': club.id,
            'icon': club.picture.location_external,
            'images': images,
            'info': {
                'active': club.is_active,
                'clubname': club.name,
                'leader': club.leader.grade_and_class
                + ' ' + club.leader.nickname,
                'loc': club.location,
                'description': club.description.raw,
                'members': len(club.members)
            }
        }

    elif action == 'searchClub':
        kw = request.args.get('keywords', '')
        search_result = Club.search(kw)
        results = [obj['_id'] for obj in search_result['results']]
        data = {
            'clubs': results
        }

    elif action == 'searchClubRandom':
        '''When the user requests for random clubs'''
        count = int(request.args['count'])
        filter = {}
        ids = [item.id for item in Club.randomclubs(count, **filter)]
        data = {
            'clubs': ids
        }

    elif action == 'getExcellentClubs':
        ids = [item.id for item in Club.excellentclubs()]
        data = {
            'clubs': ids
        }
    return jsonify(data)
