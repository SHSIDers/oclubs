#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

from flask import (
    Blueprint, render_template, url_for, session, abort, request, redirect, flash
)
from flask_login import current_user, login_required

from oclubs.objs import User, Club, Activity, Upload
import re
import math
from oclubs.enums import UserType, ClubType, ActivityTime
from oclubs.shared import get_callsign, special_access_required

actblueprint = Blueprint('actblueprint', __name__)


@actblueprint.route('/all_activities/<club_type>/<page_num>')
def allactivities(club_type, page_num):
    '''All Activities'''
    page_num = int(page_num)
    act_num = 20
    if club_type == 'all':
        acts_obj = Activity.all_activities()
        acts_obj.reverse()
    else:
        try:
            acts_obj = Activity.get_activities_conditions(club_types=[ClubType[club_type.upper()]])
            acts_obj.reverse()
        except KeyError:
            abort(404)
    max_page_num = math.ceil(float(len(acts_obj)) / act_num)
    acts_obj = acts_obj[page_num*act_num-act_num: page_num*act_num]
    return render_template('allact.html',
                           title='All Activities',
                           is_allact=True,
                           acts=acts_obj,
                           club_type=club_type,
                           page_num=page_num,
                           max_page_num=max_page_num)


@actblueprint.route('/<club>/club_activities/<page_num>')
@get_callsign(Club, 'club')
def clubactivities(club, page_num):
    '''One Club's Activities'''
    page_num = int(page_num)
    act_num = 20
    acts = club.activities([ActivityTime.UNKNOWN,
                            ActivityTime.NOON,
                            ActivityTime.AFTERSCHOOL,
                            ActivityTime.OTHERS])
    max_page_num = math.ceil(float(len(acts)) / act_num)
    acts = acts[page_num*act_num-act_num: page_num*act_num]
    club_pic = {}
    try:
        club_pic['image1'] = acts[0].pictures[0].location_external
        club_pic['image2'] = acts[1].pictures[0].location_external
        club_pic['image3'] = acts[2].pictures[0].location_external
    except IndexError:
        club_pic['image1'] = Upload(-1)
        club_pic['image2'] = Upload(-2)
        club_pic['image3'] = Upload(-3)
    return render_template('clubact.html',
                           title=club.name,
                           club=club,
                           club_pic=club_pic,
                           acts=acts,
                           page_num=page_num,
                           max_page_num=max_page_num)


@actblueprint.route('/photos/<page_num>')
def allphotos(page_num):
    page_num = int(page_num)
    pic_num = 20
    lucky_act = ''
    if page_num == 1:
        lucky_club = Club.randomclubs(1)[0]
        lucky_acts = lucky_club.activities([ActivityTime.UNKNOWN,
                                            ActivityTime.NOON,
                                            ActivityTime.AFTERSCHOOL,
                                            ActivityTime.HONGMEI,
                                            ActivityTime.OTHERS])
        if lucky_acts != []:
            lucky_act = lucky_acts[0]
        else:
            lucky_act = ''  # for testing
    acts_obj = Activity.all_activities()
    max_page_num = math.ceil(float(len(acts_obj)) / pic_num)
    acts = []
    acts_obj = acts_obj[page_num*pic_num-pic_num: page_num*pic_num]
    for i in range(pic_num / 2):
        act = {}
        try:
            act['actname1'] = acts_obj[2*i+1].name
            act['club1'] = acts_obj[2*i+1].club
            act['id1'] = acts_obj[2*i+1].id
            act['actname2'] = acts_obj[2*i].name
            act['club2'] = acts_obj[2*i].club
            act['id2'] = acts_obj[2*i].id
            act['image1'] = acts_obj[2*i+1].pictures[0].location_external
            act['image2'] = acts_obj[2*i].pictures[0].location_external
            acts.append(act)
        except IndexError:
            break
    return render_template('photos.html',
                           title='All Photos',
                           is_photos=True,
                           lucky_act=lucky_act,
                           acts=acts,
                           page_num=page_num,
                           max_page_num=max_page_num)


@actblueprint.route('/<club>/club_photo/<page_num>')
@get_callsign(Club, 'club')
def clubphoto(club, page_num):
    '''Individual Club's Photo Page'''
    page_num = int(page_num)
    pic_num = 20
    photos = []
    acts_obj = club.activities([ActivityTime.UNKNOWN,
                                ActivityTime.NOON,
                                ActivityTime.AFTERSCHOOL,
                                ActivityTime.OTHERS])
    max_page_num = math.ceil(float(len(acts_obj)) / pic_num)
    acts = []
    acts_obj = acts_obj[page_num*pic_num-pic_num: page_num*pic_num]
    for i in range(pic_num / 2):
        act = {}
        act['image1'] = acts_obj[2*i+1].pictures[0].location_external
        act['actname1'] = acts_obj[2*i+1].name
        act['id1'] = acts_obj[2*i+1].id
        act['image2'] = acts_obj[2*i].pictures[0].location_external
        act['actname2'] = acts_obj[2*i].name
        act['id2'] = acts_obj[2*i].id
        acts.append(act)
    return render_template('clubphoto.html',
                           title=club,
                           club=club,
                           photos=photos,
                           page_num=page_num,
                           max_page_num=max_page_num)


@actblueprint.route('/<club>/newact')
@get_callsign(Club, 'club')
@special_access_required
def newact(club):
    '''Hosting New Activity'''
    return render_template('newact.html',
                           title='New Activity')


@actblueprint.route('/<activity>/introduction')
@get_callsign(Activity, 'activity')
def activity(activity):
    '''Club Activity Page'''
    return render_template('activity.html',
                           title=activity.name,
                           activity=activity)


@actblueprint.route('/<club>/hongmei')
@get_callsign(Club, 'club')
@special_access_required
def hongmei(club):
    '''Check HongMei Status'''
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


@actblueprint.route('/<club>/newhm')
@get_callsign(Club, 'club')
@special_access_required
def newhm(club):
    '''Input HongMei Plan'''
    return render_template('newhm.html',
                           title='HongMei Schedule',
                           club=club.name)


@actblueprint.route('/<club>/newhm/submit', methods=['POST'])
@get_callsign(Club, 'club')
@special_access_required
def newhm_submit(club):
    '''Input HongMei plan into databse'''
    date_hm = request.form['date']
    contents = request.form['contents']
    a = Activity.new()
    a.name = contents
    a.club = get_club(club_info)
    a.description = None
    a.post = None
    a.date = date_hm
    a.time = ActivityTime.HONGMEI
    a.location = 'HongMei Elementary School'
    a.cas = 1
    return a.create()


@actblueprint.route('/<activity>/actstatus')
@get_callsign(Activity, 'activity')
@special_access_required
def actstatus(activity):
    '''Check Activity Status'''
    club = activity.club
    actname = activity.name
    date = activity.date
    intro = activity.descriptions
    members = []
    members_info = activity.signup_list()
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


@actblueprint.route('/<club>/register_hongmei')
@get_callsign(Club, 'club')
@login_required
def registerhm(club):
    '''Register Page for HongMei Activites'''
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
                           schedule=schedule)


@actblueprint.route('/<club>/register_hongmei/submit')
@get_callsign(Club, 'club')
@login_required
def registerhm_submit(club):
    '''Submit HongMei signup info to database'''
    register = request.form['register']
    for reg in register:
        act = Activity(reg)
        act.signup(current_user)
    flash('Your application has been successfully submitted.', 'reghm')
    return redirect(url_for('.registerhm', club=club.callsign))


@actblueprint.route('/<activity>/input_attendance')
@get_callsign(Activity, 'activity')
@special_access_required
def inputatten(activity):
    '''Input Attendance'''
    club = activity.club
    members_obj = activity.members
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


@actblueprint.route('/<activity>/input_attendance/submit', methods=['POST'])
@get_callsign(Activity, 'activity')
@special_access_required
def inputatten_submit(activity):
    '''Change attendance in database'''
    attendances = request.form['attendance']
    for atten in attendances:
        activity.attend(User(atten))
    flash('The attendance has been successfully submitted.', 'atten')
    return redirect(url_for('.inputatten', activity=activity.callsign))
