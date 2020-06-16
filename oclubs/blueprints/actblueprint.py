#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals, division

from datetime import date

from flask import (
    Blueprint, render_template, url_for, request, redirect, flash
)
from flask_login import current_user, login_required, fresh_login_required

from oclubs.utils.dates import today, DATE_RANGE_MAX
from oclubs.enums import UserType, ActivityTime, ResStatus
from oclubs.shared import (
    get_callsign_decorator, special_access_required, Pagination,
    render_email_template, download_xlsx, partition,
    require_student_membership, require_past_activity,
    require_future_activity, require_active_club,
    true_or_fail, form_is_valid, error_or_fail, fail, get_callsign
)
from oclubs.objs import User, Activity, Upload, FormattedText, Reservation
from oclubs.exceptions import UploadNotSupported, NoRow
from oclubs.forms.reservation_forms import PairReservation

actblueprint = Blueprint('actblueprint', __name__)


@actblueprint.route('/viewlist/<clubfilter:club_filter>/',
                    defaults={'page': 1})
@actblueprint.route('/viewlist/<clubfilter:club_filter>/<int:page>')
def allactivities(club_filter, page):
    '''All Activities'''
    act_num = 20
    count, acts = Activity.get_activities_conditions(
        limit=((page-1)*act_num, act_num),
        **club_filter.to_kwargs())
    pagination = Pagination(page, act_num, count)
    return render_template('activity/allact.html.j2',
                           is_allact=True,
                           acts=acts,
                           pagination=pagination,
                           club_filter=club_filter)


@actblueprint.route('/')
def home_redirect():
    return redirect(url_for('.allactivities', club_filter='all'))


@actblueprint.route('/photos/', defaults={'page': 1})
@actblueprint.route('/photos/<int:page>')
def allphotos(page):
    act_num = 5
    count, acts = Activity.get_activities_conditions(
        require_photos=True,
        limit=((page-1)*act_num, act_num))
    act_latest = ''
    if page == 1:
        try:
            act_latest = acts[0]
        except IndexError:
            pass
    pagination = Pagination(page, act_num, count)
    current_page = page
    template = 'activity/photos.html.j2' \
               if page == 1 else 'activity/photo-items.html.j2'
    return render_template(template,
                           is_photos=True,
                           act_latest=act_latest,
                           acts=acts,
                           pagination=pagination,
                           current_page=current_page)


@actblueprint.route('/<activity>/')
@actblueprint.route('/<activity>/introduction')
@get_callsign_decorator(Activity, 'activity')
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

    return render_template('activity/actintro.html.j2',
                           is_other_act=is_other_act,
                           has_access=has_access,
                           can_join=can_join,
                           selection=selection,
                           has_reservation=activity.has_reservation)


@actblueprint.route('/<activity>/introduction/submit', methods=['POST'])
@get_callsign_decorator(Activity, 'activity')
@login_required
@require_active_club
@require_student_membership
def actintro_submit(activity):
    '''Signup for activity'''
    if activity.selections:
        selection = request.form['selection'].strip()
        true_or_fail(selection in activity.selections,
                     'Please select a valid choice.', 'signup')
    else:
        selection = ''

    error_or_fail(lambda: activity.signup_user_status(current_user), NoRow,
                  'You have already signed up for this activity.', 'signup')

    if form_is_valid():
        activity.signup(current_user, selection=selection)
        flash('You have successfully signed up for ' + activity.name + '.',
              'signup')
    return redirect(url_for('.actintro', activity=activity.callsign))


@actblueprint.route('/<activity>/post/change')
@get_callsign_decorator(Activity, 'activity')
@special_access_required
@require_active_club
@require_past_activity
def changeactpost(activity):
    '''Page for club leader to change activity post'''
    return render_template('activity/changeactpost.html.j2')


@actblueprint.route('/<activity>/post/change/submit', methods=['POST'])
@get_callsign_decorator(Activity, 'activity')
@special_access_required
@require_active_club
@require_past_activity
def changeactpost_submit(activity):
    '''Input info into database'''
    for pic in request.files.getlist('picture'):
        if pic.filename != '':
            try:
                activity.add_picture(
                    Upload.handle(current_user, activity.club, pic))
            except UploadNotSupported:
                fail('Please upload a correct file type.', 'actpost')
                return redirect(url_for('.changeactpost',
                                        activity=activity.callsign))
    activity.post = FormattedText.handle(current_user, activity.club,
                                        request.form['post'])
    return redirect(url_for('.actintro', activity=activity.callsign))

@actblueprint.route('/<activity>/delete')
@get_callsign_decorator(Activity, 'activity')
@special_access_required        
def delete_activity(activity):
    activity.delete_activity()
    return redirect(url_for('.allactivities'))


@actblueprint.route('/<activity>/invite_hongmei')
@get_callsign_decorator(Activity, 'activity')
@require_active_club
@special_access_required
@require_future_activity
def hongmei_invite(activity):
    '''Allow club leader to invite members to hongmei activy'''
    return render_template('activity/invitehm.html.j2')


@actblueprint.route('/<activity>/invite_hongmei/submit', methods=['POST'])
@get_callsign_decorator(Activity, 'activity')
@require_active_club
@special_access_required
@require_future_activity
def hongmei_invite_submit(activity):
    '''Input invitation result into database'''
    invite = request.form.getlist('invite')
    for each in invite:
        member = User(each)
        true_or_fail(member in activity.club.members, member.nickname +
                     ' is not a member of this club.', 'invite_hm')
        if form_is_valid():
            activity.signup(member)
            parameters = {'member': member, 'activity': activity}
            contents = render_email_template('invitehm', parameters)
            member.email_user('HongMei Invitation - ' + activity.club.name,
                              contents)
            member.notify_user('You have been invited to HongMei activity - ' +
                               activity.name + ' on ' +
                               activity.date.strftime('%b-%d-%y') + '.')
    flash('These members have been successfully invited.', 'invite_hm')
    return redirect(url_for('.hongmei_invite', activity=activity.callsign))


@actblueprint.route('/<activity>/signup_status')
@get_callsign_decorator(Activity, 'activity')
@require_active_club
@special_access_required
@require_future_activity
def actstatus(activity):
    '''Check Activity Status'''
    return render_template('activity/actstatus.html.j2')


@actblueprint.route('/<activity>/signup_status/submit', methods=['POST'])
@get_callsign_decorator(Activity, 'activity')
@require_active_club
@special_access_required
@require_future_activity
def actstatus_submit(activity):
    '''Change consent form status'''
    member = User(request.form['uid'])
    true_or_fail(member in activity.club.members, member.nickname +
                 ' is not a member of this club.', 'consent_form')

    if form_is_valid():
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
@get_callsign_decorator(Activity, 'activity')
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


@actblueprint.route('/<activity>/change_activity_info')
@get_callsign_decorator(Activity, 'activity')
@special_access_required
def changeactinfo(activity):
    '''Allow club leaders to change activity info'''
    years = (lambda m: map(lambda n: m + n, range(2)))(date.today().year)
    cas = int(activity.cas)
    return render_template('/activity/changeactinfo.html.j2',
                           is_allact=True,
                           years=years,
                           act_types=ActivityTime,
                           cas=cas)


@actblueprint.route('/<activity>/change_activity_info/submit',
                    methods=['POST'])
@get_callsign_decorator(Activity, 'activity')
@special_access_required
def changeactinfo_submit(activity):
    '''Input change in activity info into database'''
    actname = request.form['name']
    if not actname:
        fail('Please input the name of the activity.', 'actinfo')
        return redirect(url_for('.changeactinfo', activity=activity.callsign))
    if actname != activity.name:
        activity.name = actname

    desc = request.form['description'].strip()
    if desc != activity.description.raw:
        activity.description = FormattedText.handle(
            current_user,
            activity.club,
            request.form['description'])
    try:
        actdate = date(int(request.form['year']),
                       int(request.form['month']),
                       int(request.form['day']))
    except ValueError:
        fail('Invalid date.', 'actinfo')
        return redirect(url_for('.changeactinfo', activity=activity.callsign))
    if actdate < date.today():
        fail('Please choose the correct date.', 'actinfo')
        return redirect(url_for('.changeactinfo', activity=activity.callsign))
    activity.date = actdate

    time = ActivityTime[request.form['act_type'].upper()]
    activity.time = time
    activity.location = request.form['location']
    time_type = request.form['time_type']
    try:
        cas = int(request.form['cas'])
    except ValueError:
        fail('Invalid CAS hours.', 'actinfo')
        return redirect(url_for('.changeactinfo', activity=activity.callsign))
    if cas < 0:
        fail('Invalid CAS hours.', 'actinfo')
        return redirect(url_for('.changeactinfo', activity=activity.callsign))
    if time_type == 'hours':
        activity.cas = cas
    else:
        activity.cas = cas / 60

    for member in activity.signup_list():
        member['user'].notify_user('%s\'s information has been changed.'
                                   % activity.name)
    return redirect(url_for('.actintro', activity=activity.callsign))


@actblueprint.route('/<activity>/pairreservation', methods=['GET', 'POST'])
@get_callsign_decorator(Activity, 'activity')
@special_access_required
def pairreservation(activity):
    reservations = Reservation.get_reservations_conditions(
        status=ResStatus.UNPAIRED,
        reserver_club=activity.club,
        dates=(today(), DATE_RANGE_MAX)
    )

    form = PairReservation()

    if reservations:
        choices = []
        for reservation in reservations:
            if reservation.activity is None:
                choices.append((
                    reservation.callsign,
                    "%s %s: %s" % (reservation.date,
                                   reservation.timeslot.format_name,
                                   reservation.classroom.location)
                ))
        form.reservations_for_pairing.choices = choices

    if request.method == 'POST':
        if form.check():
            selected_reservation = get_callsign(
                Reservation,
                str(form.reservations_for_pairing.data))

            selected_reservation.status = ResStatus.PAIRED
            selected_reservation.activity = activity

            if activity.reservation is None:
                activity.reservation = selected_reservation
            else:
                activity.reservation.activity = None
                activity.reservation.status = ResStatus.UNPAIRED
                activity.reservation = selected_reservation

            activity.date = selected_reservation.date
            activity.time = selected_reservation.timeslot
            activity.location = selected_reservation.classroom.location

            return redirect(url_for(
                '.actintro',
                activity=selected_reservation.activity.callsign))
        else:
            return render_template('/activity/pairreservation.html.j2',
                                   form=form)

    return render_template('/activity/pairreservation.html.j2',
                           form=form)


@actblueprint.route('/<activity>/attendance')
@get_callsign_decorator(Activity, 'activity')
@special_access_required
@require_past_activity
def attendance(activity):
    '''Check attendance'''
    attend, absent = partition(lambda member: member in activity.attendance,
                               activity.club.members)
    return render_template('/activity/attendance.html.j2',
                           attend=attend,
                           absent=absent)


@actblueprint.route('/<activity>/attendance/submit', methods=['POST'])
@get_callsign_decorator(Activity, 'activity')
@special_access_required
@require_past_activity
def attendance_submit(activity):
    '''Submit change in attendance'''
    ids = request.form.getlist('attendance')
    members = map(User, ids)
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
@get_callsign_decorator(Activity, 'activity')
@special_access_required
def attendance_download(activity):
    '''Download activity's attendance'''
    result = []
    result.append(('Nick Name', 'Class', 'Attendance'))
    attend, absent = partition(lambda member: member in activity.attendance,
                               activity.club.members)

    result.extend([(member.nickname, member.grade_and_class, 'Attended')
                   for member in attend])
    result.extend([(member.nickname, member.grade_and_class, 'Absent')
                   for member in absent])
    return download_xlsx('Attendance for ' + activity.name + '.xlsx', result)


@actblueprint.route('/info_download_all')
@special_access_required
@fresh_login_required
def allactivitiesinfo():
    '''Allow admin to download all activities' info'''
    info = []
    info.append(('Activity ID', 'Name', 'Club', 'Club Leader', 'Club Leader\'s Class',
                 'Date', 'Time (Type)', 'Location', 'CAS Hours', '# of attendance'))
    info.extend([(act.id, act.name, act.club.name, act.club.leader.passportname,
                  act.club.leader.grade_and_class, act.date.strftime('%b-%d-%y'),
                  act.time.format_name, act.location, act.cas, len(act.attendance))
                for act in Activity.all_activities()])
    return download_xlsx('All Activities\' Info.xlsx', info)


@actblueprint.route('/info_download_thisweek')
@special_access_required
@fresh_login_required
def thisweek_activitiesinfo():
    '''Allow admin to download this week's activities' info'''
    info = []
    info.append(('Activity ID', 'Name', 'Club', 'Club Leader', 'Club Leader\'s Class',
                 'Date', 'Time (Type)', 'Location', 'CAS Hours'))
    info.extend([(act.id, act.name, act.club.name, act.club.leader.passportname,
                  act.club.leader.grade_and_class, act.date.strftime('%b-%d-%y'),
                  act.time.format_name, act.location, act.cas)
                for act in Activity.thisweek_activities()])
    return download_xlsx('This week\'s Activities\' Info.xlsx', info)


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
        fail('You have input wrong date for HongMei schedule.', 'status_info')
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
    return download_xlsx('HongMei\'s Schedule on ' +
                         actdate.strftime('%b-%d-%Y') + '.xlsx', info)
