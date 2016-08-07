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
import traceback

from oclubs.enums import UserType, ClubType, ActivityTime
from oclubs.shared import get_callsign, special_access_required, Pagination, download_xlsx, render_email_template
from oclubs.objs import User, Club, Activity, Upload, FormattedText

actblueprint = Blueprint('actblueprint', __name__)


@actblueprint.route('/all_activities/<club_type>/<int:page>')
def allactivities(club_type, page):
    '''All Activities'''
    act_num = 20
    if club_type == 'all':
        acts_obj = Activity.get_activities_conditions(limit=((page-1)*act_num, act_num))
        count = acts_obj[0]
        acts = acts_obj[1]
    else:
        try:
            acts_obj = Activity.get_activities_conditions(club_types=[ClubType[club_type.upper()]], limit=((page-1)*act_num, act_num))
            count = acts_obj[0]
            acts = acts_obj[1]
        except KeyError:
            abort(404)
    pagination = Pagination(page, act_num, count)
    return render_template('activity/allact.html',
                           title='All Activities',
                           is_allact=True,
                           acts=acts,
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
    club_pic = []
    for upload in club.allactphotos():
        club_pic.append(upload)
        if len(club_pic) == 3:
            break
    if len(club_pic) < 3:
        for miss in range(3 - len(club_pic)):
            club_pic.append(Upload(-101))
    return render_template('activity/clubact.html',
                           title=club.name,
                           club=club,
                           club_pic=club_pic,
                           acts=acts,
                           pagination=pagination)


@actblueprint.route('/photos/<int:page>')
def allphotos(page):
    pic_num = 20
    acts_obj = Activity.get_activities_conditions(require_photos=True,
                                                  limit=((page-1)*pic_num, pic_num))
    acts = acts_obj[1]
    if page == 1:
        try:
            act_recent = acts[0]
        except IndexError:
            act_recent = ''
    pagination = Pagination(page, pic_num, acts_obj[0])
    return render_template('activity/photos.html',
                           title='All Photos',
                           is_photos=True,
                           act_recent=act_recent,
                           acts=acts,
                           pagination=pagination)


@actblueprint.route('/<club>/club_photo/<int:page>')
@get_callsign(Club, 'club')
def clubphoto(club, page):
    '''Individual Club's Photo Page'''
    pic_num = 20
    uploads = club.allactphotos()
    pagination = Pagination(page, pic_num, len(uploads))
    uploads = uploads[(page-1)*pic_num-pic_num: page*pic_num]
    return render_template('activity/clubphoto.html',
                           title=club.name,
                           uploads=uploads,
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
            a.description = FormattedText(0)
        a.post = FormattedText(0)
        a.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        a.time = ActivityTime[request.form['act_type'].upper()]
        a.location = request.form['location']
        time_type = request.form['time_type']
        if time_type == 'hours':
            a.cas = int(request.form['cas'])
        else:
            a.cas = int(request.form['cas']) / 60
        a.create()
        flash(a.name + ' has been successfully created.', 'newact')
    except ValueError:
        flash('Please input all information to create a new activity.', 'newact')
    else:
        for member in club.members:
            parameters = {'member': member, 'club': club, 'act': activity}
            contents = render_email_template('newact', parameters)
            # member.email_user('HongMei Plan - ' + club.name, contents)
    return redirect(url_for('.newact', club=club.callsign))


@actblueprint.route('/<activity>/introduction')
@get_callsign(Activity, 'activity')
def activity(activity):
    '''Club Activity Page'''
    if current_user.is_authenticated:
        has_access = (current_user == activity.club.leader or
                      current_user == activity.club.teacher or
                      current_user.type == UserType.ADMIN)
    else:
        has_access = False
    is_other_act = (activity.time == ActivityTime.UNKNOWN or
                    activity.time == ActivityTime.OTHERS)
    return render_template('activity/actintro.html',
                           title=activity.name,
                           is_other_act=is_other_act,
                           is_past=date.today() >= activity.date,
                           has_access=has_access)


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


@actblueprint.route('/<activity>/change_activity_post')
@get_callsign(Activity, 'activity')
@special_access_required
def changeactpost(activity):
    '''Page for club leader to change activity post'''
    return render_template('activity/changeactpost.html',
                           title='Change Activity Post',
                           act=activity)


@actblueprint.route('/<activity>/change_activity_post/submit', methods=['POST'])
@get_callsign(Activity, 'activity')
@special_access_required
def changeactpost_submit(activity):
    '''Input info into database'''
    if request.files['picture'].filename != '':
        # for pic in request.files['picture']:
        print request.files['picture']
        activity.add_picture(Upload.handle(current_user, activity.club, request.files['picture']))
    if request.form['post'] != '':
        print request.form['post']
        activity.post = FormattedText.handle(current_user, activity.club, request.form['post'])
    flash('Activity post has been successfully modified.', 'actpost')
    return redirect(url_for('.changeactpost', activity=activity.callsign))


@actblueprint.route('/<club>/hongmei_status')
@get_callsign(Club, 'club')
@special_access_required
def hongmei_status(club):
    '''Check HongMei Status'''
    acts = club.activities([ActivityTime.HONGMEI], (False, True))
    return render_template('activity/hmstatus.html',
                           title='HongMei Status',
                           acts=acts)


@actblueprint.route('/<club>/hongmei_status/download')
@get_callsign(Club, 'club')
@special_access_required
def hongmei_status_download(club):
    '''Download HongMei status'''
    result = []
    result.append(['Date', 'Members'])
    hongmei = club.activities([ActivityTime.HONGMEI], (False, True))
    for each in hongmei:
        result_each = []
        result_each.append(each.date.strftime('%b-%d-%y'))
        members = each.signup_list()
        members_result = ''
        for member in members:
            if member['consentform'] == 0:
                consentform = 'No'
            else:
                consentform = 'Yes'
            members_result += member['user'].nickname + ': ' \
                + str(member['user'].phone) + ' (Consent From Handed? ' \
                + consentform + ')\n'
        result_each.append(members_result)
        result.append(result_each)
    return download_xlsx('HongMei Status - ' + club.name + '.xlsx', result)


@actblueprint.route('/<club>/new_hongmei_schedule')
@get_callsign(Club, 'club')
@special_access_required
def newhm(club):
    '''Input HongMei Plan'''
    return render_template('activity/newhm.html',
                           title='HongMei Schedule',
                           club=club.name)


@actblueprint.route('/<club>/new_hongmei_schedule/submit', methods=['POST'])
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
    result = []
    result.append(['Nick Name', 'Student ID', 'Attendance'])
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
    return download_xlsx('Attendance for ' + activity.name + '.xlsx', result)
