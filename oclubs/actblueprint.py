#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals, division

from flask import (
    Blueprint, render_template, url_for, session, abort, request, redirect, flash
)
from flask_login import current_user, login_required

import re
import math
from copy import deepcopy
from datetime import datetime, date

from oclubs.enums import UserType, ClubType, ActivityTime
from oclubs.shared import get_callsign, special_access_required, Pagination, download_csv
from oclubs.objs import User, Club, Activity, Upload, FormattedText

actblueprint = Blueprint('actblueprint', __name__)


@actblueprint.route('/all_activities/<club_type>/<int:page>')
def allactivities(club_type, page):
    '''All Activities'''
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

    pagination = Pagination(page, act_num, len(acts_obj))
    acts_obj = acts_obj[(page-1)*act_num: page*act_num]
    return render_template('activity/allact.html',
                           title='All Activities',
                           is_allact=True,
                           acts=acts_obj,
                           club_type=club_type,
                           pagination=pagination)


@actblueprint.route('/<club>/club_activities/<int:page>')
@get_callsign(Club, 'club')
def clubactivities(club, page):
    '''One Club's Activities'''
    act_num = 20
    acts = club.activities([ActivityTime.UNKNOWN,
                            ActivityTime.NOON,
                            ActivityTime.AFTERSCHOOL,
                            ActivityTime.OTHERS])

    pagination = Pagination(page, act_num, len(acts))
    acts = acts[(page-1)*act_num: page*act_num]
    club_pic = {}
    try:
        club_pic['image1'] = acts[0].pictures[0].location_external
        club_pic['image2'] = acts[1].pictures[0].location_external
        club_pic['image3'] = acts[2].pictures[0].location_external
    except IndexError:
        club_pic['image1'] = Upload(-1)
        club_pic['image2'] = Upload(-2)
        club_pic['image3'] = Upload(-3)
    return render_template('activity/clubact.html',
                           title=club.name,
                           club=club,
                           club_pic=club_pic,
                           acts=acts,
                           pagination=pagination)

@actblueprint.route('/photos/<int:page>')
def allphotos(page):
    pic_num = 20
    acts_obj = Activity.all_activities()
    act_recent = ''
    if page == 1:
        for act in acts_obj:
            try:
                assert act.pictures[0].location_external
                act_recent = act
            except IndexError:
                continue
            else:
                break
    acts = []
    for act in acts_obj:
        try:
            assert act.pictures[0]
        except IndexError:
            continue
        acts.append(act)
    all_pictures = []
    for act in acts:
        each_block = {}
        each_block['activity'] = act
        each_block['club'] = act.club
        for pic in act.pictures:
            each = deepcopy(each_block)
            each['picture'] = pic
            all_pictures.append(each)

    pagination = Pagination(page, pic_num, len(all_pictures))
    acts = acts[(page-1)*pic_num: page*pic_num]
    return render_template('activity/photos.html',
                           title='All Photos',
                           is_photos=True,
                           act_recent=act_recent,
                           all_pictures=all_pictures,
                           pagination=pagination)


@actblueprint.route('/<club>/club_photo/<int:page>')
@get_callsign(Club, 'club')
def clubphoto(club, page):
    '''Individual Club's Photo Page'''
    pic_num = 20
    photos = []
    acts_obj = club.activities([ActivityTime.UNKNOWN,
                                ActivityTime.NOON,
                                ActivityTime.AFTERSCHOOL,
                                ActivityTime.OTHERS])

    pagination = Pagination(page, pic_num, len(acts_obj))
    acts = []
    acts_obj = acts_obj[(page-1)*pic_num-pic_num: page*pic_num]
    for i in range(pic_num / 2):
        act = {}
        try:
            act['image1'] = acts_obj[2*i+1].pictures[0].location_external
            act['image2'] = acts_obj[2*i].pictures[0].location_external
        except IndexError:
            break
        act['actname1'] = acts_obj[2*i+1].name
        act['id1'] = acts_obj[2*i+1].id
        act['actname2'] = acts_obj[2*i].name
        act['id2'] = acts_obj[2*i].id
        acts.append(act)
    return render_template('activity/clubphoto.html',
                           title=club.name,
                           club=club,
                           photos=photos,
                           pagination=pagination)


@actblueprint.route('/<club>/newact')
@get_callsign(Club, 'club')
@special_access_required
def newact(club):
    '''Hosting New Activity'''
    return render_template('activity/newact.html',
                           title='New Activity')


@actblueprint.route('/<club>/newact/submit', methods=['POST'])
@get_callsign(Club, 'club')
@special_access_required
def newact_submit(club):
    '''Input new activity's information into database'''
    try:
        a = Activity.new()
        a.name = request.form['name']
        a.club = club
        if request.form['description']:
            a.description = FormattedText.handle(current_user, club, request.form['description'])
        else:
            a.description = None
        a.post = None
        a.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        a.time = ActivityTime[request.form['act_type'].upper()]
        a.location = request.form['location']
        a.cas = request.form['cas']
        a.create()
        flash(a.name + ' has been successfully created.', 'newact')
    except ValueError:
        flash('Please input all information to create a new activity.', 'newact')
    return redirect(url_for('.newact', club=club.callsign))


@actblueprint.route('/<activity>/introduction')
@get_callsign(Activity, 'activity')
def activity(activity):
    '''Club Activity Page'''
    return render_template('activity/actintro.html',
                           title=activity.name,
                           is_other_act=(activity.time == ActivityTime.UNKNOWN or
                                         activity.time == ActivityTime.OTHERS),
                           is_past=date.today() >= activity.date,
                           has_access=(current_user == activity.club.leader or
                                       current_user == activity.club.teacher or
                                       current_user.type == UserType.ADMIN))


@actblueprint.route('/<activity>/introduction/submit', methods=['POST'])
@get_callsign(Activity, 'activity')
@login_required
def activity_submit(activity):
    '''Signup for activity'''
    activity.signup(current_user)
    flash('You have successfully signed up for ' + activity.name + '.', 'signup')
    return redirect(url_for('.activity', activity=activity.callsign))


@actblueprint.route('/<activity>/post')
@get_callsign(Activity, 'activity')
def actpost(activity):
    '''Activity Post Page'''
    return render_template('activity/actpost.html',
                           title='Activity Post')


@actblueprint.route('/<club>/hongmei_status')
@get_callsign(Club, 'club')
@special_access_required
def hongmei_status(club):
    '''Check HongMei Status'''
    acts = club.activities([ActivityTime.HONGMEI], (False, True))
    return render_template('activity/hmstatus.html',
                           title='HongMei Status',
                           acts=acts)


@actblueprint.route('/<club>/newhm')
@get_callsign(Club, 'club')
@special_access_required
def newhm(club):
    '''Input HongMei Plan'''
    return render_template('activity/newhm.html',
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
    a.club = club
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
    members_num = 0
    for member in activity.signup_list():
        members_num += 1
    return render_template('activity/actstatus.html',
                           title=activity.name,
                           activity=activity,
                           members_num=members_num)


@actblueprint.route('/<activity>/input_attendance')
@get_callsign(Activity, 'activity')
@special_access_required
def inputatten(activity):
    '''Input Attendance'''
    return render_template('activity/inputatten.html',
                           title='Input Attendance',
                           activity=activity)


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


@actblueprint.route('/<activity>/check_attendance')
@get_callsign(Activity, 'activity')
@special_access_required
def checkatten(activity):
    '''Check attendance'''
    attendance = activity.attendance
    attend = []
    absent = []
    for member in activity.signup_list():
        if member['user'] in attendance:
            attend.append(member['user'])
        else:
            absent.append(member['user'])
    return render_template('/activity/checkatten.html',
                           title='Check Attendance',
                           activity=activity,
                           attend=attend,
                           absent=absent)


@actblueprint.route('/<activity>/check_attendance/download')
@get_callsign(Activity, 'activity')
@special_access_required
def checkatten_download(activity):
    '''Download activity's attendance'''
    header = ['Nick Name', 'Student ID', 'Attendance']
    result = []
    attendance = activity.attendance
    attend = []
    absent = []
    for member in activity.signup_list():
        if member['user'] in attendance:
            attend.append(member['user'])
        else:
            absent.append(member['user'])
    for member in attend:
        result_each = []
        result_each.append(member.nickname)
        result_each.append(member.studentid)
        result_each.append('Attended')
        result.append(result_each)
    for member in absent:
        result_each = []
        result_each.append(member.nickname)
        result_each.append(member.studentid)
        result_each.append('Absent')
        result.append(result_each)
    return download_csv('Attendance for ' + activity.name + '.csv', header, result)
