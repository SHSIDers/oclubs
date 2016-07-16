#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from flask import (
    Blueprint, render_template, url_for, session, abort
)

import traceback
import oclubs
import re

actblueprint = Blueprint('actblueprint', __name__)


@actblueprint.route('/allact')
def allactivities():
    '''All Activities'''
    user = ''
    activities = [{'club_name': 'Art Club', 'act_name': 'Painting', 'time': 'June 30, 2016', 'place': 'Art Center'},
                  {'club_name': 'Photo Club', 'act_name': 'Taking Pictures', 'time': 'June 30, 2016', 'place': 'SHSID Campus'},
                  {'club_name': 'Art Club', 'act_name': 'Painting', 'time': 'June 30, 2016', 'place': 'Art Center'},
                  {'club_name': 'Photo Club', 'act_name': 'Taking Pictures', 'time': 'June 30, 2016', 'place': 'SHSID Campus'},
                  {'club_name': 'Art Club', 'act_name': 'Painting', 'time': 'June 30, 2016', 'place': 'Art Center'},
                  {'club_name': 'Photo Club', 'act_name': 'Taking Pictures', 'time': 'June 30, 2016', 'place': 'SHSID Campus'},
                  {'club_name': 'Art Club', 'act_name': 'Painting', 'time': 'June 30, 2016', 'place': 'Art Center'},
                  {'club_name': 'Photo Club', 'act_name': 'Taking Pictures', 'time': 'June 30, 2016', 'place': 'SHSID Campus'},
                  {'club_name': 'Art Club', 'act_name': 'Painting', 'time': 'June 30, 2016', 'place': 'Art Center'},
                  {'club_name': 'Photo Club', 'act_name': 'Taking Pictures', 'time': 'June 30, 2016', 'place': 'SHSID Campus'},
                  {'club_name': 'Art Club', 'act_name': 'Painting', 'time': 'June 30, 2016', 'place': 'Art Center'},
                  {'club_name': 'Photo Club', 'act_name': 'Taking Pictures', 'time': 'June 30, 2016', 'place': 'SHSID Campus'}]
    return render_template('allact.html',
                           title='All Activities',
                           is_allact=True,
                           user=user,
                           activities=activities)


@actblueprint.route('/<club_info>/clubact')
def clubactivities(club_info):
    '''One Club's Activities'''
    if('user_id' in session):
        user_obj = oclubs.objs.User(session['user_id'])
        user = user_obj.nickname
    else:
        user = ''
    try:
        club_id = int(re.match(r'^\d+', club_info).group(0))
        club = oclubs.objs.Club(club_id)
    except:
        abort(404)
    club_info = {}
    club_info['club_name'] = club.name

    # get past activities' pictures
    club_info = {'club_name': 'Art Club', 'image1': '1', 'image2': '2', 'image3': '3'}
    activities = []
    activities_obj = club.activities([True, True, True, False, True])
    for activity_obj in activities_obj:
        activity = {}
        activity['act_name'] = activity_obj.name
        activity_date = str(activity_obj.date)
        activity['time'] = activity_date[0:4] + " - " + activity_date[4:6] + " - " + activity_date[6:8]
        # activity['place']  = 
        activities.append(activity)
    return render_template('clubact.html',
                           title=club['club_name'],
                           user=user,
                           club=club_info,
                           activities=activities)


@actblueprint.route('/photos')
def allphotos():
    user = ''
    top = {'image': 'intro5', 'actname': 'Making Website', 'club': 'Website Club'}
    photos = [{'image1': 'intro1', 'actname1': 'Random Activity', 'club1': 'Random Club', 'image2': 'intro2', 'actname2': 'Random Activity', 'club2': 'Random Club'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'club1': 'Random Club', 'image2': 'intro2', 'actname2': 'Random Activity', 'club2': 'Random Club'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'club1': 'Random Club', 'image2': 'intro2', 'actname2': 'Random Activity', 'club2': 'Random Club'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'club1': 'Random Club', 'image2': 'intro2', 'actname2': 'Random Activity', 'club2': 'Random Club'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'club1': 'Random Club', 'image2': 'intro2', 'actname2': 'Random Activity', 'club2': 'Random Club'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'club1': 'Random Club', 'image2': 'intro2', 'actname2': 'Random Activity', 'club2': 'Random Club'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'club1': 'Random Club', 'image2': 'intro2', 'actname2': 'Random Activity', 'club2': 'Random Club'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'club1': 'Random Club', 'image2': 'intro2', 'actname2': 'Random Activity', 'club2': 'Random Club'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'club1': 'Random Club', 'image2': 'intro2', 'actname2': 'Random Activity', 'club2': 'Random Club'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'club1': 'Random Club', 'image2': 'intro2', 'actname2': 'Random Activity', 'club2': 'Random Club'}]
    return render_template('photos.html',
                           title='All Photos',
                           is_photos=True,
                           user=user,
                           top=top,
                           photos=photos)


@actblueprint.route('/<club_info>/newact')
def newact(club_info):
    '''Hosting New Activity'''
    if('user_id' in session):
        user_obj = oclubs.objs.User(session['user_id'])
        user = user_obj.nickname
    else:
        user = ''
    try:
        club_id = int(re.match(r'^\d+', club_info).group(0))
        club = oclubs.objs.Club(club_id)
    except:
        abort(404)
    return render_template('newact.html',
                           title='New Activity',
                           user=user)


@actblueprint.route('/act')
def activity():
    '''Club Activity Page'''
    user = ''
    activity = {'club': 'Website Club', 'actname': 'Making Website',
                'time': 'June 6, 2016', 'people': '20-30', 'intro': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'}
    return render_template('activity.html',
                           title=activity['actname'],
                           user=user,
                           activity=activity)


@actblueprint.route('/hongmei')
def hongmei():
    '''Check HongMei Status'''
    user = ''
    club = 'Website Club'
    schedule = [{'date': 'June 6, 2016', 'members': [{'name': 'Derril', 'phone': '18918181818'},
                                                     {'name': 'Frank', 'phone': '18918181818'},
                                                     {'name': 'YiFei', 'phone': '18918181818'}]},
                {'date': 'June 6, 2016', 'members': [{'name': 'Derril', 'phone': '18918181818'},
                                                     {'name': 'Frank', 'phone': '18918181818'},
                                                     {'name': 'YiFei', 'phone': '18918181818'}]},
                {'date': 'June 6, 2016', 'members': [{'name': 'Derril', 'phone': '18918181818'},
                                                     {'name': 'Frank', 'phone': '18918181818'},
                                                     {'name': 'YiFei', 'phone': '18918181818'}]}]
    return render_template('hongmei.html',
                           title='HongMei',
                           user=user,
                           club=club,
                           schedule=schedule)


@actblueprint.route('/newhm')
def newhm():
    '''Input HongMei Plan'''
    user = ''
    club = 'Website Club'
    return render_template('newhm.html',
                           title='HongMei Schedule',
                           user=user,
                           club=club)


@actblueprint.route('/<act_info>/actstatus')
def actstatus(act_info):
    '''Check Activity Status'''
    if 'user_id' not in session:
        abort(401)
    user_obj = oclubs.objs.User(session['user_id'])
    try:
        act_id = int(re.match(r'^\d+', act_info).group(0))
        act = oclubs.objs.Activity(act_id)
        club = act.club
    except:
        abort(404)
    if user_obj.id != club.leader.id:
        abort(403)
    actname = act.name
    date_str = str(act.date)
    date = date_str[:4] + " - " + date_str[4:6] + " - " + date_str[6:8]
    intro = act.descriptions
    members = [{'name': 'Derril', 'email': 'lolol@outlook.com', 'phone': '18918181818'},
               {'name': 'Frank', 'email': 'lolol@outlook.com', 'phone': '18918181818'},
               {'name': 'YiFei', 'email': 'lolol@outlook.com', 'phone': '18918181818'}]
    members_num = 0
    for member in members:
        members_num += 1
    return render_template('actstatus.html',
                           title=actname,
                           user=user_obj.nickname,
                           club=club.name,
                           actname=actname,
                           date=date,
                           intro=intro,
                           members=members,
                           members_num=members_num)


@actblueprint.route('/<club_info>/register_hongmei')
def registerhm(club_info):
    '''Register Page for HongMei Activites'''
    if 'user_id' not in session:
        abort(401)
    user_obj = oclubs.objs.User(session['user_id'])
    try:
        club_id = int(re.match(r'^\d+', club_info).group(0))
        club = oclubs.objs.Club(club_id)
    except:
        abort(404)
    schedule = []
    # activities = club.
    schedule = [{'id': '1', 'date': 'June 6 2016', 'activity': 'Finish homepage design'},
                {'id': '2', 'date': 'June 7 2016', 'activity': 'Finish activity page design'},
                {'id': '3', 'date': 'June 8 2016', 'activity': 'Finish personal page design'},
                {'id': '4', 'date': 'June 9 2016', 'activity': 'Finish club page design'},
                {'id': '5', 'date': 'June 10 2016', 'activity': 'Finish photo page design'},
                {'id': '6', 'date': 'June 11 2016', 'activity': 'Finish about page design'},
                {'id': '7', 'date': 'June 6 2016', 'activity': 'Finish homepage design'},
                {'id': '8', 'date': 'June 7 2016', 'activity': 'Finish activity page design'},
                {'id': '9', 'date': 'June 8 2016', 'activity': 'Finish personal page design'},
                {'id': '10', 'date': 'June 9 2016', 'activity': 'Finish club page design'},
                {'id': '11', 'date': 'June 10 2016', 'activity': 'Finish photo page design'},
                {'id': '12', 'date': 'June 11 2016', 'activity': 'Finish about page design'},
                {'id': '13', 'date': 'June 6 2016', 'activity': 'Finish homepage design'},
                {'id': '14', 'date': 'June 7 2016', 'activity': 'Finish activity page design'},
                {'id': '15', 'date': 'June 8 2016', 'activity': 'Finish personal page design'},
                {'id': '16', 'date': 'June 9 2016', 'activity': 'Finish club page design'},
                {'id': '17', 'date': 'June 10 2016', 'activity': 'Finish photo page design'},
                {'id': '18', 'date': 'June 11 2016', 'activity': 'Finish about page design'}]
    return render_template('registerhm.html',
                           title='Register for HongMei',
                           user=user_obj.nickname,
                           club=club.name,
                           schedule=schedule)


@actblueprint.route('/<act_info>/register_hongmei_submit')
def registerhm_submit(act_info):
    '''Submit HongMei signup info to database'''
    pass
