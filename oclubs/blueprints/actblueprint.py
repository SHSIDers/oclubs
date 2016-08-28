#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals, division

from datetime import date

from flask import (
    Blueprint, render_template, url_for, abort, request, redirect, flash
)
from flask_login import current_user, login_required, fresh_login_required

from oclubs.enums import UserType, ClubType, ActivityTime
from oclubs.shared import (
    get_callsign, special_access_required, Pagination, render_email_template,
    download_xlsx, partition, require_membership, require_past_activity
)
from oclubs.objs import User, Activity, Upload, FormattedText
from oclubs.exceptions import UploadNotSupported, NoRow

actblueprint = Blueprint('actblueprint', __name__)


@actblueprint.route('/all/<club_type>/', defaults={'page': 1})
@actblueprint.route('/all/<club_type>/<int:page>')
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


@actblueprint.route('/photos/', defaults={'page': 1})
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


@actblueprint.route('/<activity>/')
def actredirect(activity):
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
            can_join = False
            selection = activity.signup_user_status(current_user)['selection']
        except NoRow:
            selection = ''
            can_join = (current_user.type == UserType.STUDENT)
    else:
        can_join = False
        has_access = False
        selection = ''

    is_other_act = activity.time in [ActivityTime.UNKNOWN, ActivityTime.OTHERS]
    return render_template('activity/actintro.html',
                           is_other_act=is_other_act,
                           is_past=date.today() >= activity.date,
                           has_access=has_access,
                           can_join=can_join,
                           selection=selection)


@actblueprint.route('/<activity>/introduction/submit', methods=['POST'])
@get_callsign(Activity, 'activity')
@login_required
@require_membership
def actintro_submit(activity):
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
@require_past_activity
def actpost(activity):
    '''Activity Post Page'''
    return render_template('activity/actpost.html')


@actblueprint.route('/<activity>/post/change')
@get_callsign(Activity, 'activity')
@special_access_required
@require_past_activity
def changeactpost(activity):
    '''Page for club leader to change activity post'''
    return render_template('activity/changeactpost.html')


@actblueprint.route('/<activity>/post/change/submit', methods=['POST'])
@get_callsign(Activity, 'activity')
@special_access_required
@require_past_activity
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
    activity.post = FormattedText.handle(current_user, activity.club,
                                         request.form['post'])
    flash('Activity post has been successfully modified.', 'actpost')
    return redirect(url_for('.changeactpost', activity=activity.callsign))


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
        member.email_user('HongMei Invitation - ' + activity.club.name,
                          contents)
        member.notify_user('You have been invited to HongMei activity - ' +
                           activity.name + ' on ' +
                           activity.date.strftime('%b-%d-%y') + '.')
    flash('These members have been successfully invited.', 'invite_hm')
    return redirect(url_for('.hongmei_invite', activity=activity.callsign))


@actblueprint.route('/<activity>/signup_status')
@get_callsign(Activity, 'activity')
@special_access_required
def actstatus(activity):
    '''Check Activity Status'''
    members_num = 0
    for member in activity.signup_list():
        members_num += 1
    return render_template('activity/actstatus.html',
                           members_num=members_num)


@actblueprint.route('/<activity>/signup_status/submit', methods=['POST'])
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


@actblueprint.route('/<activity>/signup_status/download')
@get_callsign(Activity, 'activity')
@special_access_required
def actstatus_download(activity):
    '''Download activity status'''
    info = []
    info.append(['Nick Name', 'Email', 'Phone', 'Consent Form',
                 'Selection' if activity.selections else ''])
    info.extend([(member['user'].nickname,
                  member['user'].email,
                  str(member['user'].phone),
                  'Handed in' if member['consentform'] == 1
                  else 'Not handed in',
                  member['selection'] if activity.selections else '')
                for member in activity.signup_list()])
    return download_xlsx('Activity Status - ' + activity.name + '.xlsx', info)


@actblueprint.route('/<activity>/attendance')
@get_callsign(Activity, 'activity')
@special_access_required
def attendance(activity):
    '''Check attendance'''
    attend, absent = partition(lambda member: member in activity.attendance,
                               activity.club.members)
    return render_template('/activity/attendance.html',
                           attend=attend,
                           absent=absent)


@actblueprint.route('/<activity>/attendance/submit', methods=['POST'])
@get_callsign(Activity, 'activity')
@special_access_required
def attendance_submit(activity):
    '''Submit change in attendance'''
    ids = request.form.getlist('attendance')
    members = []
    members.extend([(User(each)) for each in ids])
    attend, absent = partition(lambda member: member in activity.attendance,
                               activity.club.members)
    for member in members:
        if member in absent:
            activity.attend(member)
        elif member in attend:
            activity.attend_undo(member)
    flash('The change in attendance has been submitted.', 'attendance')
    return redirect(url_for('.attendance', activity=activity.callsign))


@actblueprint.route('/<activity>/attendance/download')
@get_callsign(Activity, 'activity')
@special_access_required
def attendance_download(activity):
    '''Download activity's attendance'''
    result = []
    result.append(('Nick Name', 'Student ID', 'Attendance'))
    attend, absent = partition(lambda member: member in activity.attendance,
                               activity.club.members)

    result.extend([(member.nickname, member.studentid, 'Attended')
                   for member in attend])
    result.extend([(member.nickname, member.studentid, 'Absent')
                   for member in absent])
    return download_xlsx('Attendance for ' + activity.name + '.xlsx', result)


@actblueprint.route('/info_download_all')
@special_access_required
@fresh_login_required
def allactivitiesinfo():
    '''Allow admin to download all activities' info'''
    info = []
    info.append(('Activity ID', 'Name', 'Club', 'Date', 'Time (Type)',
                 'Location', 'CAS Hours'))
    info.extend([(act.id, act.name, act.club.name,
                  act.date.strftime('%b-%d-%y'), act.time.format_name,
                  act.location, act.cas) for act in Activity.all_activities()])

    return download_xlsx('All Activities\' Info.xlsx', info)


@actblueprint.route('/check_hongmei_schedule/download', methods=['POST'])
@special_access_required
def checkhongmeischedule_download():
    '''Allow admin to check HongMei schedule'''
    info = []
    try:
        actdate = date(int(request.form['year']),
                       int(request.form['month']),
                       int(request.form['day']))
    except ValueError:
        flash('You have input wrong date for HongMei schedule.', 'status_info')
        return redirect(url_for('userblueprint.personal'))
    info.append((actdate.strftime('%b-%d-%Y'),))
    info.append(('Club Name', 'Members'))
    for act in Activity.get_activities_conditions(
                    times=(ActivityTime.HONGMEI,),
                    dates=actdate
                ):
        members = ''

        members = '\n'.join((member['user'].nickname + ': ' +
                             str(member['user'].phone) +
                             '(Consent From Handed? ' +
                             ('Yes' if member['consentform'] == 1 else 'No') +
                             ')')
                            for member in act.signup_list())
        info.append((act.club.name, members))
    return download_xlsx('HongMei\'s Schedule on' +
                         date.strftime('%b-%d-%Y') + '.xlsx', info)
