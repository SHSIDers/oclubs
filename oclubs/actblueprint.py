#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from flask import (
    Blueprint, render_template, url_for, session, abort, request, redirect, flash
)

import oclubs
import re

actblueprint = Blueprint('actblueprint', __name__)


def date_to_string(date):
    date_str = str(date)
    result = date_str[:4] + " - " + date_str[4:6] + " - " + date_str[6:8]
    return result


@actblueprint.route('/all')
def allactivities():
    '''All Activities'''
    activities = []
    acts_obj = oclubs.objs.Activity.all_activities()
    for act_obj in acts_obj:
        act = {}
        act['club_name'] = act_obj.club.name
        act['act_name'] = act_obj.name
        act['time'] = date_to_string(act_obj.date)
        act['place'] = act_obj.location
        activities.append(act)
    return render_template('allact.html',
                           title='All Activities',
                           is_allact=True,
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
        club_obj = oclubs.objs.Club(club_id)
    except:
        abort(404)
    club = {}
    club['club_name'] = club_obj.name

    # get past activities' pictures
    club = {'club_name': 'Art Club', 'image1': '1', 'image2': '2', 'image3': '3'}
    activities = []
    activities_obj = club_obj.activities([True, True, True, False, True])
    for act_obj in activities_obj:
        activity = {}
        activity['act_name'] = act_obj.name
        activity['time'] = date_to_string(act_obj.date)
        activity['place'] = act_obj.location
        activities.append(activity)
    return render_template('clubact.html',
                           title=club['club_name'],
                           club=club,
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
                           club=club,
                           photos=photos)


@actblueprint.route('/<club_info>/newact')
def newact(club_info):
    '''Hosting New Activity'''
    if 'user_id' not in session:
        abort(401)
    user_obj = oclubs.objs.User(session['user_id'])
    try:
        club_id = int(re.match(r'^\d+', club_info).group(0))
        club = oclubs.objs.Club(club_id)
    except:
        abort(404)
    if user_obj.id != club.leader.id:
        abort(403)
    return render_template('newact.html',
                           title='New Activity')


@actblueprint.route('/<act_info>/introduction')
def activity(act_info):
    '''Club Activity Page'''
    try:
        act_id = int(re.match(r'^\d+', act_info).group(0))
        act_obj = oclubs.objs.Activity(act_id)
    except:
        abort(404)
    act = {}
    act['club'] = act_obj.club.name
    act['actname'] = act_obj.name
    act['time'] = date_to_string(act_obj.date)
    act['intro'] = act_obj.description
    return render_template('activity.html',
                           title=activity['actname'],
                           activity=act)


@actblueprint.route('/<club_info>/hongmei')
def hongmei(club_info):
    '''Check HongMei Status'''
    if 'user_id' not in session:
        abort(401)
    user_obj = oclubs.objs.User(session['user_id'])
    try:
        club_id = int(re.match(r'^\d+', club_info).group(0))
        club = oclubs.objs.Club(club_id)
    except:
        abort(404)
    if user_obj.id != club.leader.id:
        abort(403)
    schedule = []
    acts_obj = club.activities((False, False, False, True, False), (False, True))
    for act_obj in acts_obj:
        act = {}
        act['date'] = act.date_to_string(act_obj.date)
        members = []
        members_list = act_obj.signup_list()
        for member_list in members_list:
            member = {}
            member_obj = member_list.user
            member['name'] = member_obj.nickname
            member['phone'] = member_obj.phone
            member['consentform'] = member_obj.consentform
            members.append(member)
        act['members'] = members
        schedule.append(act)
    return render_template('hongmei.html',
                           title='HongMei',
                           club=club.name,
                           schedule=schedule)


@actblueprint.route('/<club_info>/newhm')
def newhm(club_info):
    '''Input HongMei Plan'''
    if 'user_id' not in session:
        abort(401)
    user_obj = oclubs.objs.User(session['user_id'])
    try:
        club_id = int(re.match(r'^\d+', club_info).group(0))
        club = oclubs.objs.Club(club_id)
    except:
        abort(404)
    if user_obj.id != club.leader.id:
        abort(403)
    return render_template('newhm.html',
                           title='HongMei Schedule',
                           club=club.name,
                           club_info=club_info)


@actblueprint.route('/<club_info>/newhm/submit', methods=['POST'])
def newhm_submit(club_info):
    '''Input HongMei plan into databse'''
    date = request.form['date']
    contents = request.form['contents']
    pass


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
    date = date_to_string(act.date)
    intro = act.descriptions
    members = []
    members_info = act.signup_list()
    for member_info in members_info:
        member = {}
        member_obj = member_info['user']
        member['name'] = member_obj.nickname
        member['email'] = member_obj.email
        member['phone'] = member_obj.phone
        member['consentform'] = member_info['consentform']
        members.append(member)
    members_num = 0
    for member in members:
        members_num += 1
    return render_template('actstatus.html',
                           title=actname,
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
        act['date'] = date_to_string(act_obj.date)
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
    user_obj = oclubs.objs.User(session['user_id'])
    register = request.form['register']
    for reg in register:
        act = oclubs.objs.Activity(reg)
        act.signup(user_obj)
    flash('Your application has been successfully submitted.', 'reghm')
    return redirect(url_for('.registerhm', club_info=club_info))


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
    return redirect(url_for('.inputatten', act_info=act_info))
