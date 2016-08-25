#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals, division

from datetime import date

from flask import (
    Blueprint, render_template, url_for, abort, request, redirect, flash
)
from flask_login import current_user, login_required

from oclubs.enums import UserType, ClubType, ActivityTime
from oclubs.shared import (
    get_callsign, special_access_required, Pagination, render_email_template,
    download_xlsx, partition
)
from oclubs.objs import User, Club, Activity, Upload, FormattedText
from oclubs.exceptions import UploadNotSupported, AlreadyExists, NoRow

actblueprint = Blueprint('actblueprint', __name__)


@actblueprint.route('/all_activities/<club_type>/<int:page>')
def allactivities(club_type, page):
    '''All Activities'''
    act_num = 20
    if club_type == 'all':
        count, acts = Activity.get_activities_conditions(
            limit=((page-1)*act_num, act_num))
    else:
        try:
            count, acts = Activity.get_activities_conditions(
                club_types=[ClubType[club_type.upper()]],
                limit=((page-1)*act_num, act_num))
        except KeyError:
            abort(404)
    pagination = Pagination(page, act_num, count)
    return render_template('activity/allact.html',
                           is_allact=True,
                           acts=acts,
                           club_type=club_type,
                           pagination=pagination)


@actblueprint.route('/<club>/club_activities/<int:page>')
@get_callsign(Club, 'club')
def clubactivities(club, page):
    '''One Club's Activities'''
    act_num = 20
    acts = club.activities()

    pagination = Pagination(page, act_num, len(acts))
    acts = acts[(page-1)*act_num: page*act_num]
    club_pic = []
    club_pic.extend(club.allactphotos(limit=3)[1])
    club_pic.extend([Upload(-101) for _ in range(3 - len(club_pic))])
    return render_template('activity/clubact.html',
                           club_pic=club_pic,
                           acts=acts,
                           pagination=pagination)


@actblueprint.route('/photos/<int:page>')
def allphotos(page):
    pic_num = 20
    count, acts = Activity.get_activities_conditions(
        require_photos=True,
        limit=((page-1)*pic_num, pic_num))
    act_recent = ''
    if page == 1:
        try:
            act_recent = acts[0]
        except IndexError:
            pass
    pagination = Pagination(page, pic_num, count)
    return render_template('activity/photos.html',
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
                           uploads=uploads,
                           pagination=pagination)


@actblueprint.route('/<club>/newact')
@get_callsign(Club, 'club')
@special_access_required
def newact(club):
    '''Hosting New Activity'''
    years = (lambda m: map(lambda n: m + n, range(2)))(date.today().year)
    return render_template('activity/newact.html',
                           years=years)


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
            a.description = FormattedText.handle(current_user, club,
                                                 request.form['description'])
        else:
            a.description = FormattedText(0)
        a.post = FormattedText(0)
        actdate = date(int(request.form['year']),
                       int(request.form['month']),
                       int(request.form['day']))
        if actdate < date.today():
            raise IndexError
        a.date = actdate
        time = ActivityTime[request.form['act_type'].upper()]
        a.time = time
        a.location = request.form['location']
        time_type = request.form['time_type']
        if time_type == 'hours':
            a.cas = int(request.form['cas'])
        else:
            a.cas = int(request.form['cas']) / 60
        if (time == ActivityTime.OTHERS or time == ActivityTime.UNKNOWN) and \
                request.form['has_selection'] == 'yes':
            choices = request.form['selections'].split(';')
            a.selections = [choice.strip(' ') for choice in choices]
        else:
            a.selections = []
        a.create()
        flash(a.name + ' has been successfully created.', 'newact')
    except ValueError:
        flash('Please input all information to create a new activity.',
              'newact')
    except IndexError:
        flash('Please choose the correct date.', 'newact')
    else:
        for member in club.members:
            parameters = {'member': member, 'club': club, 'act': a}
            contents = render_email_template('newact', parameters)
            member.email_user(a.name + ' - ' + club.name, contents)
            member.notify_user(club.name + ' is going to host ' + a.name + '.')
    return redirect(url_for('.newact', club=club.callsign))


@actblueprint.route('/<activity>/')
def clubredirect(activity):
    return redirect(url_for('.actintro', activity=activity))


@actblueprint.route('/<activity>/introduction')
@get_callsign(Activity, 'activity')
def actintro(activity):
    '''Club Activity Page'''
    if current_user.is_authenticated:
        has_access = (current_user == activity.club.leader or
                      current_user == activity.club.teacher or
                      current_user.type == UserType.ADMIN)
        try:
            selection = activity.signup_user_status(current_user)['selection']
            can_join = (current_user.type == UserType.STUDENT)
        except NoRow:
            selection = ''
            can_join = False
    else:
        can_join = False
        has_access = False
        selection = ''
    is_other_act = (activity.time == ActivityTime.UNKNOWN or
                    activity.time == ActivityTime.OTHERS)
    return render_template('activity/actintro.html',
                           is_other_act=is_other_act,
                           is_past=date.today() >= activity.date,
                           has_access=has_access,
                           can_join=can_join,
                           selection=selection)


@actblueprint.route('/<activity>/introduction/submit', methods=['POST'])
@get_callsign(Activity, 'activity')
@login_required
def activity_submit(activity):
    '''Signup for activity'''
    if activity.selections:
        activity.signup(current_user, selection=request.form['selection'])
    else:
        activity.signup(current_user)
    flash('You have successfully signed up for ' + activity.name + '.',
          'signup')
    return redirect(url_for('.actintro', activity=activity.callsign))


@actblueprint.route('/<activity>/post')
@get_callsign(Activity, 'activity')
def actpost(activity):
    '''Activity Post Page'''
    return render_template('activity/actpost.html')


@actblueprint.route('/<activity>/change_activity_post')
@get_callsign(Activity, 'activity')
@special_access_required
def changeactpost(activity):
    '''Page for club leader to change activity post'''
    return render_template('activity/changeactpost.html')


@actblueprint.route('/<activity>/change_activity_post/submit',
                    methods=['POST'])
@get_callsign(Activity, 'activity')
@special_access_required
def changeactpost_submit(activity):
    '''Input info into database'''
    for pic in request.files.getlist('picture'):
        if pic.filename != '':
            try:
                activity.add_picture(
                    Upload.handle(current_user, activity.club, pic))
            except UploadNotSupported:
                flash('Please upload a correct file type.', 'actpost')
                return redirect(url_for('.changeactpost',
                                        activity=activity.callsign))
    if request.form['post'] != '':
        activity.post = FormattedText.handle(current_user, activity.club,
                                             request.form['post'])
    flash('Activity post has been successfully modified.', 'actpost')
    return redirect(url_for('.changeactpost', activity=activity.callsign))


@actblueprint.route('/<club>/hongmei_status')
@get_callsign(Club, 'club')
@special_access_required
def hongmei_status(club):
    '''Check HongMei Status'''
    acts = club.activities([ActivityTime.HONGMEI], (False, True))
    return render_template('activity/hmstatus.html',
                           acts=acts)


@actblueprint.route('/<activity>/invite_hongmei')
@get_callsign(Activity, 'activity')
@special_access_required
def hongmei_invite(activity):
    '''Allow club leader to invite members to hongmei activy'''
    return render_template('activity/invitehm.html')


@actblueprint.route('/<activity>/invite_hongmei/submit', methods=['POST'])
@get_callsign(Activity, 'activity')
@special_access_required
def hongmei_invite_submit(activity):
    '''Input invitation result into database'''
    invite = request.form.getlist('invite')
    plan = ''
    for each in invite:
        member = User(each)
        activity.signup(member)
        parameters = {'member': member, 'activity': activity, 'plan': plan}
        contents = render_email_template('invitehm', parameters)
        member.email_user('HongMei Invitation - ' + activity.club.name, contents)
        member.notify_user('You have been invited to HongMei activity - ' +
                           activity.name + ' on ' +
                           activity.date.strftime('%b-%d-%y') + '.')
    flash('These members have been successfully invited.', 'invite_hm')
    return redirect(url_for('.hongmei_invite', activity=activity.callsign))


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
    acts = club.activities([ActivityTime.HONGMEI], (False, True))
    years = (lambda m: map(lambda n: m + n, range(2)))(date.today().year)
    return render_template('activity/newhm.html',
                           acts=acts,
                           years=years)


@actblueprint.route('/<club>/new_hongmei_schedule/submit', methods=['POST'])
@get_callsign(Club, 'club')
@special_access_required
def newhm_submit(club):
    '''Input HongMei plan into databse'''
    contents = request.form['contents']
    try:
        actdate = date(int(request.form['year']),
                       int(request.form['month']),
                       int(request.form['day']))
    except ValueError:
        flash('Please input valid date to submit.', 'newhm')
        return redirect(url_for('.newhm', club=club.callsign))
    if contents == '' or actdate < date.today():
        flash('Please input contents or correct date to submit.', 'newhm')
        return redirect(url_for('.newhm', club=club.callsign))
    a = Activity.new()
    a.name = contents
    a.club = club
    a.description = FormattedText.emptytext()
    a.date = actdate
    a.time = ActivityTime.HONGMEI
    a.location = 'HongMei Elementary School'
    a.cas = 1
    a.post = FormattedText.emptytext()
    a.create()
    return redirect(url_for('.newhm', club=club.callsign))


@actblueprint.route('/<activity>/actstatus')
@get_callsign(Activity, 'activity')
@special_access_required
def actstatus(activity):
    '''Check Activity Status'''
    members_num = 0
    for member in activity.signup_list():
        members_num += 1
    return render_template('activity/actstatus.html',
                           members_num=members_num)


@actblueprint.route('/<activity>/actstatus/submit', methods=['POST'])
@get_callsign(Activity, 'activity')
@special_access_required
def actstatus_submit(activity):
    '''Change consent form status'''
    member = User(request.form['studentid'])
    status = int(request.form['status'])
    if status == 0:
        activity.signup(member, consentform=True)
        flash(member.nickname + ' has handed in the consent form.',
              'consent_form')
    elif status == 1:
        activity.signup(member, consentform=False)
        flash(member.nickname + ' has not handed in the consent form.',
              'consent_form')
    return redirect(url_for('.actstatus', activity=activity.callsign))


@actblueprint.route('/<activity>/actstatus/download')
@get_callsign(Activity, 'activity')
@special_access_required
def actstatus_download(activity):
    '''Download activity status'''
    info = []
    if activity.selections:
        info.append(['Nick Name', 'Email', 'Phone', 'Consent Form', 'Selection'])
        info.extend([(member['user'].nickname,
                      member['user'].email,
                      str(member['user'].phone),
                      'Handed in' if member['consentform'] == 1
                      else 'Not handed in',
                      member['selection'])
                    for member in activity.signup_list()])
    else:
        info.append(['Nick Name', 'Email', 'Phone', 'Consent Form'])
        info.extend([(member['user'].nickname,
                      member['user'].email,
                      str(member['user'].phone),
                      'Handed in' if member['consentform'] == 1
                      else 'Not handed in')
                    for member in activity.signup_list()])
    return download_xlsx('Activity Status - ' + activity.name + '.xlsx', info)


@actblueprint.route('/<activity>/input_attendance')
@get_callsign(Activity, 'activity')
@special_access_required
def inputatten(activity):
    '''Input Attendance'''
    return render_template('activity/inputatten.html')


@actblueprint.route('/<activity>/input_attendance/submit', methods=['POST'])
@get_callsign(Activity, 'activity')
@special_access_required
def inputatten_submit(activity):
    '''Change attendance in database'''
    attendances = request.form.getlist('attendance')
    if attendances == []:
        flash('Please select the people who attended the activity.', 'atten')
    else:
        for atten in attendances:
            try:
                activity.attend(User(atten))
            except AlreadyExists:
                pass
        flash('The attendance has been successfully submitted.', 'atten')
    return redirect(url_for('.inputatten', activity=activity.callsign))


@actblueprint.route('/<activity>/check_attendance')
@get_callsign(Activity, 'activity')
@special_access_required
def checkatten(activity):
    '''Check attendance'''
    attendance = activity.attendance
    attend, absent = partition(activity.signup_list(),
                               lambda member: member['user'] in attendance)
    return render_template('/activity/checkatten.html',
                           attend=attend,
                           absent=absent)


@actblueprint.route('/<activity>/check_attendance/download')
@get_callsign(Activity, 'activity')
@special_access_required
def checkatten_download(activity):
    '''Download activity's attendance'''
    result = []
    result.append(('Nick Name', 'Student ID', 'Attendance'))
    attendance = activity.attendance
    attend, absent = partition(activity.signup_list(),
                               lambda member: member['user'] in attendance)

    result.append([(member.nickname, member.studentid, 'Attended')
                   for member in attend])
    result.append([(member.nickname, member.studentid, 'Absent')
                   for member in absent])
    return download_xlsx('Attendance for ' + activity.name + '.xlsx', result)
