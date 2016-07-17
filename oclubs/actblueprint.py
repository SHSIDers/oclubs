#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from flask import (
    Blueprint, render_template, url_for, session, abort, request, redirect, flash
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


@actblueprint.route('/<club_info>/activity')
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


@actblueprint.route('/<club_info>/photo')
def clubphoto(club_info):
    '''Individual Club's Photo Page'''
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
    club_name = club.name
    photos = []
    activities_obj = club.activities([True, True, True, False, True])
    photos = [{'image1': 'intro1', 'actname1': 'Random Activity', 'image2': 'intro2', 'actname2': 'Random Activity'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'image2': 'intro2', 'actname2': 'Random Activity'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'image2': 'intro2', 'actname2': 'Random Activity'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'image2': 'intro2', 'actname2': 'Random Activity'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'image2': 'intro2', 'actname2': 'Random Activity'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'image2': 'intro2', 'actname2': 'Random Activity'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'image2': 'intro2', 'actname2': 'Random Activity'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'image2': 'intro2', 'actname2': 'Random Activity'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'image2': 'intro2', 'actname2': 'Random Activity'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'image2': 'intro2', 'actname2': 'Random Activity'}]
    return render_template('clubphoto.html',
                           title=club,
                           user=user,
                           club=club,
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
    try:
        club_id = int(re.match(r'^\d+', club_info).group(0))
        club = oclubs.objs.Club(club_id)
    except:
        abort(404)
    schedule = []
    acts_obj = club.activities((False, False, False, True, False), (False, True))
    for act_obj in acts_obj:
        act = {}
        act['id'] = act_obj.id
        date = str(act_obj.date)
        act['date'] = date[0:4] + " - " + date[4:6] + " - " + date[6:8]
        act['activity'] = act_obj.description
        schedule.append(act)
    return render_template('registerhm.html',
                           title='Register for HongMei',
                           club=club.name,
                           schedule=schedule,
                           club_info=club_info)


@actblueprint.route('/<club_info>/register_hongmei/submit')
def registerhm_submit(club_info):
    '''Submit HongMei signup info to database'''
    club_id = int(re.match(r'^\d+', club_info).group(0))
    club = oclubs.objs.Club(club_id)
    user_obj = oclubs.objs.User(session['user_id'])
    register = request.form['register']
    for reg in register:
        act = oclubs.objs.Activity(reg)
        act.signup(user_obj)
    flash('Your application has been successfully submitted.', 'reghm')
    return redirect(url_for('registerhm', club_info=club_info))


@actblueprint.route('/<act_info>/input_attendance')
def inputatten(act_info):
    '''Input Attendance'''
    if 'user_id' not in session:
        abort(401)
    user_obj = oclubs.objs.User(session['user_id'])
    try:
        act_id = int(re.match(r'^\d+', act_info).group(0))
        act = oclubs.objs.Activity(act_id)
    except:
        abort(404)
    club = act.club
    if user_obj.id != club.leader.id:
        abort(403)
    members_obj = act.members
    members = []
    for member_obj in members_obj:
        member = {}
        member['passportname'] = member_obj.passportname
        member['nick_name'] = member_obj.nickname
        member['picture'] = member_obj.picture
        member['id'] = member_obj.id
        members.append(member)
    return render_template('inputatten.html',
                           title='Input Attendance',
                           club=club.name,
                           members=members)


@actblueprint.route('/<act_info>/input_attendance/submit', methods=['POST'])
def inputatten_submit(act_info):
    '''Change attendance in database'''
    act_id = int(re.match(r'^\d+', act_info).group(0))
    act = oclubs.objs.Activity(act_id)
    attendances = request.form['attendance']
    for atten in attendances:
        act.attend(oclubs.objs.User(atten))
    flash('The attendance has been successfully submitted.', 'atten')
    return redirect(url_for('inputatten', act_info=act_info))
