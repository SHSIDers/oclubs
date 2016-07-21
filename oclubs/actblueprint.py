#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

from flask import (
    Blueprint, render_template, url_for, session, abort, request, redirect, flash
)

from oclubs.objs import User, Club, Activity
import re
import math
from oclubs.enums import UserType, ClubType, ActivityTime
from oclubs.shared import get_club, get_act

actblueprint = Blueprint('actblueprint', __name__)


@actblueprint.route('/all_activities/<club_type>/<page_num>')
def allactivities(club_type, page_num):
    '''All Activities'''
    page_num = int(page_num)
    act_num = 20
    if club_type == 'all':
        acts_obj = Activity.all_activities()
        acts_obj.reverse()
    elif club_type:
        acts_obj = Activity.get_activities_conditions(club_types=[ClubType[club_type.upper()]])
        acts_obj.reverse()
    max_page_num = math.ceil(float(len(acts_obj)) / act_num)
    acts_obj = acts_obj[page_num*act_num-act_num: page_num*act_num]
    return render_template('allact.html',
                           title='All Activities',
                           is_allact=True,
                           acts=acts_obj,
                           club_type=club_type,
                           page_num=page_num,
                           max_page_num=max_page_num)


@actblueprint.route('/<club_info>/club_activities')
def clubactivities(club_info):
    '''One Club's Activities'''
    club_obj = get_club(club_info)
    club = {}
    club['club_name'] = club_obj.name

    # get past activities' pictures
    club = {'club_name': 'Art Club', 'image1': '1', 'image2': '2', 'image3': '3'}
    activities = []
    activities_obj = club_obj.activities([ActivityTime.UNKNOWN,
                                          ActivityTime.NOON,
                                          ActivityTime.AFTERSCHOOL,
                                          ActivityTime.OTHERS])
    for act_obj in activities_obj:
        activity = {}
        activity['act_name'] = act_obj.name
        activity['time'] = act_obj.date
        activity['place'] = act_obj.location
        activities.append(activity)
    return render_template('clubact.html',
                           title=club['club_name'],
                           club=club,
                           activities=activities)


@actblueprint.route('/photos')
def allphotos():
    lucky_club = Club.randomclubs(1)[0]
    lucky_act = lucky_club.activities([ActivityTime.UNKNOWN,
                                       ActivityTime.NOON,
                                       ActivityTime.AFTERSCHOOL,
                                       ActivityTime.HONGMEI,
                                       ActivityTime.OTHERS])[0]
    acts_obj = Activity.all_activities[:20]
    acts = []
    for i in range(10):
        act = {}
        act['image1'] = acts_obj[2*i+1].pictures[0].location_external
        act['actname1'] = acts_obj[2*i+1].name
        act['club1'] = acts_obj[2*i+1].club
        act['id1'] = acts_obj[2*i+1].id
        act['image2'] = acts_obj[2*i].pictures[0].location_external
        act['actname2'] = acts_obj[2*i].name
        act['club2'] = acts_obj[2*i].club
        act['id2'] = acts_obj[2*i].id
        acts.append(act)
    return render_template('photos.html',
                           title='All Photos',
                           is_photos=True,
                           lucky_act=lucky_act,
                           acts=acts)


@actblueprint.route('/<club_info>/photo')
def clubphoto(club_info):
    '''Individual Club's Photo Page'''
    club = get_club(club_info)
    club_name = club.name
    photos = []
    activities_obj = club.activities([ActivityTime.UNKNOWN,
                                      ActivityTime.NOON,
                                      ActivityTime.AFTERSCHOOL,
                                      ActivityTime.OTHERS])
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
    user_obj = User(session['user_id'])
    club = get_club(club_info)
    if user_obj.id != club.leader.id:
        abort(403)
    return render_template('newact.html',
                           title='New Activity')


@actblueprint.route('/<act_info>/introduction')
def activity(act_info):
    '''Club Activity Page'''
    act_obj = get_act(act_info)
    act = {}
    act['club'] = act_obj.club.name
    act['actname'] = act_obj.name
    act['time'] = act_obj.date
    act['intro'] = act_obj.description
    return render_template('activity.html',
                           title=activity['actname'],
                           activity=act)


@actblueprint.route('/<club_info>/hongmei')
def hongmei(club_info):
    '''Check HongMei Status'''
    if 'user_id' not in session:
        abort(401)
    user_obj = User(session['user_id'])
    club = get_club(club_info)
    if user_obj != club.leader and user_obj != club.teacher:
        abort(403)
    schedule = []
    acts_obj = club.activities([ActivityTime.HONGMEI], (False, True))
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
    user_obj = User(session['user_id'])
    club = get_club(club_info)
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
    user_obj = User(session['user_id'])
    act = get_act(act_info)
    club = act.club
    if user_obj.id != club.leader.id:
        abort(403)
    actname = act.name
    date = act.date
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
    club = get_club(club_info)
    schedule = []
    acts_obj = club.activities([ActivityTime.HONGMEI], (False, True))
    for act_obj in acts_obj:
        act = {}
        act['id'] = act_obj.id
        act['date'] = act_obj.date
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
    user_obj = User(session['user_id'])
    register = request.form['register']
    for reg in register:
        act = Activity(reg)
        act.signup(user_obj)
    flash('Your application has been successfully submitted.', 'reghm')
    return redirect(url_for('.registerhm', club_info=club_info))


@actblueprint.route('/<act_info>/input_attendance')
def inputatten(act_info):
    '''Input Attendance'''
    if 'user_id' not in session:
        abort(401)
    user_obj = User(session['user_id'])
    act = get_act(act_info)
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
    act = get_act(act_info)
    attendances = request.form['attendance']
    for atten in attendances:
        act.attend(User(atten))
    flash('The attendance has been successfully submitted.', 'atten')
    return redirect(url_for('.inputatten', act_info=act_info))
