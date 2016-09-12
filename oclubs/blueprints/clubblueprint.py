#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals, division

from datetime import date

from flask import (
    Blueprint, render_template, url_for, request, redirect, flash, abort
)
from flask_login import current_user, login_required, fresh_login_required

from oclubs.objs import Activity, User, Club, Upload, FormattedText
from oclubs.enums import UserType, ClubType, ClubJoinMode, ActivityTime
from oclubs.shared import (
    download_xlsx, get_callsign, special_access_required,
    render_email_template, Pagination, require_active_club,
    require_student_membership, require_membership, require_not_student,
    true_or_fail, form_is_valid, fail
)
from oclubs.exceptions import UploadNotSupported, AlreadyExists, NoRow
from oclubs.access import siteconfig

clubblueprint = Blueprint('clubblueprint', __name__)


@clubblueprint.route('/list/<clubfilter:club_filter>')
def clublist(club_filter):
    '''Club list by club type'''
    num = 18
    clubs = Club.randomclubs(num, **club_filter.to_kwargs())
    return render_template('club/clublist.html',
                           is_list=True,
                           clubs=clubs,
                           club_filter=club_filter)


@clubblueprint.route('/<club>/manage')
@get_callsign(Club, 'club')
@require_active_club
@special_access_required
def club(club):
    '''Club Management Page'''
    return render_template('club/clubmanage.html')


@clubblueprint.route('/<club>/')
@clubblueprint.route('/<club>/introduction')
@get_callsign(Club, 'club')
def clubintro(club):
    '''Club Intro'''
    free_join = (current_user.is_active and
                 club.joinmode == ClubJoinMode.FREE_JOIN and
                 current_user.type == UserType.STUDENT and
                 current_user not in club.members)
    see_email = (current_user.type == UserType.ADMIN or current_user == club.leader)
    return render_template('club/clubintro.html',
                           free_join=free_join,
                           see_email=see_email)


@clubblueprint.route('/<club>/introduction/submit', methods=['POST'])
@get_callsign(Club, 'club')
@login_required
@require_active_club
def clubintro_submit(club):
    '''Add new member'''
    true_or_fail(current_user.type == UserType.STUDENT,
                 'You may not join clubs.', 'join')
    true_or_fail(club.joinmode == ClubJoinMode.FREE_JOIN,
                 'You may not join this club.', 'join')
    if form_is_valid():
        try:
            club.add_member(current_user)
        except AlreadyExists:
            fail('You are already in %s.' % club.name, 'join')
            return redirect(url_for('.clubintro', club=club.callsign))
        parameters = {'club': club, 'current_user': current_user}
        contents = render_email_template('joinclubs', parameters)
        club.leader.email_user('New Club Member - ' + club.name, contents)
        club.leader.notify_user('%s has joined %s.'
                                % (current_user.nickname, club.name))
        flash('You have successfully joined ' + club.name + '.', 'join')
    return redirect(url_for('.clubintro', club=club.callsign))


@clubblueprint.route('/<club>/new_leader')
@get_callsign(Club, 'club')
@require_active_club
@special_access_required
@fresh_login_required
def newleader(club):
    '''Selecting New Club Leader'''
    return render_template('club/newleader.html')


@clubblueprint.route('/<club>/new_leader/submit', methods=['POST'])
@get_callsign(Club, 'club')
@require_active_club
@special_access_required
@fresh_login_required
def newleader_submit(club):
    '''Change leader in database'''
    leader_old = club.leader
    members_obj = club.members
    leader_name = request.form['leader']
    for member_obj in members_obj:
        if leader_name == member_obj.passportname:
            club.leader = member_obj
            break
    else:
        assert False, 'wtf?'
    for member in club.teacher_and_members:
        parameters = {'user': member, 'club': club, 'leader_old': leader_old}
        contents = render_email_template('newleader', parameters)
        member.email_user('New Leader - ' + club.name, contents)
        member.notify_user(club.leader.nickname +
                           ' becomes the new leader of ' + club.name + '.')
    return render_template('club/success.html')


@clubblueprint.route('/<club>/member_info')
@get_callsign(Club, 'club')
@require_membership
def memberinfo(club):
    '''Check Members' Info'''
    has_access = (current_user == club.leader or
                  current_user == club.teacher or
                  current_user.type == UserType.ADMIN)
    return render_template('club/memberinfo.html',
                           has_access=has_access)


@clubblueprint.route('/<club>/member_info/notify_members', methods=['POST'])
@get_callsign(Club, 'club')
@require_active_club
@special_access_required
def memberinfo_notify_members(club):
    '''Allow club leader to notify members'''
    contents = request.form['contents']
    if contents == '':
        flash('Please input something.', 'notify_members')
        return redirect(url_for('.memberinfo', club=club.callsign))
    for member in club.members:
        member.notify_user(contents)
        parameters = {'member': member, 'club': club, 'notify_contents': contents}
        contents = render_email_template('notifymembers', parameters)
        member.email_user('Notification - ' + club.name, contents)
    flash('You have successfully notified members.', 'notify_members')
    return redirect(url_for('.memberinfo', club=club.callsign))


@clubblueprint.route('/<club>/member_info/download')
@get_callsign(Club, 'club')
@require_membership
@special_access_required
def memberinfo_download(club):
    '''Download members' info'''
    info = []
    info.append(('Nick Name', 'Class', 'Passport Name', 'Email'))
    info.extend([(member.nickname, member.grade_and_class, member.passportname,
                  member.email) for member in club.members])
    return download_xlsx('Member Info.xlsx', info)


@clubblueprint.route('/<club>/change_info')
@get_callsign(Club, 'club')
@require_active_club
@special_access_required
def changeclubinfo(club):
    '''Change Club's Info'''
    return render_template('club/changeclubinfo.html')


@clubblueprint.route('/<club>/change_info/submit', methods=['POST'])
@get_callsign(Club, 'club')
@require_active_club
@special_access_required
def changeclubinfo_submit(club):
    '''Change club's info'''
    intro = request.form['intro']
    if len(intro) > 90:
        fail('Your intro is too long.', 'clubinfo')
        return redirect(url_for('.changeclubinfo', club=club.callsign))
    elif request.form['intro'] != '':
        club.intro = request.form['intro']

    desc = request.form['description'].strip()
    if desc and desc != club.description.raw:
        club.description = FormattedText.handle(current_user, club,
                                                request.form['description'])
    if request.files['picture'].filename != '':
        try:
            club.picture = Upload.handle(current_user, club,
                                         request.files['picture'])
        except UploadNotSupported:
            fail('Please upload the correct file type.', 'clubinfo')
            return redirect(url_for('.changeclubinfo', club=club.callsign))
    teacher_email = request.form['email']
    if teacher_email != club.teacher.studentid:
        club.teacher = User.find_teacher(teacher_email)
    location = request.form['location']
    if location != club.location and location != '':
        club.location = location
    for member in club.teacher_and_members:
        parameters = {'user': member, 'club': club}
        contents = render_email_template('changeclubinfo', parameters)
        member.email_user('Change Club Info - ' + club.name, contents)
        member.notify_user(club.name + '\'s information has been changed.')
    flash('The information about club has been successfully submitted.',
          'clubinfo')
    return redirect(url_for('.changeclubinfo', club=club.callsign))


@clubblueprint.route('/<club>/adjust_member')
@get_callsign(Club, 'club')
@require_active_club
@special_access_required
@fresh_login_required
def adjustmember(club):
    '''Adjust Club Members'''
    invite_member = club.joinmode == ClubJoinMode.BY_INVITATION
    return render_template('club/adjustmember.html',
                           invite_member=invite_member)


@clubblueprint.route('/<club>/adjust_member/submit', methods=['POST'])
@get_callsign(Club, 'club')
@require_active_club
@special_access_required
@fresh_login_required
def adjustmember_submit(club):
    '''Input adjustment of club members'''
    member = User(request.form['uid'])
    true_or_fail(current_user != member,
                 'You cannot expel yourself.', 'expelled')
    if form_is_valid():
        club.remove_member(member)
        parameters = {'member': member, 'club': club}
        contents = render_email_template('adjustmember', parameters)
        member.email_user('Member Adjustment - ' + club.name, contents)
        member.notify_user('You have been moved out of ' + club.name + '.')
        flash(member.nickname + ' has been expelled.', 'expelled')
    return redirect(url_for('.adjustmember', club=club.callsign))


@clubblueprint.route('/<club>/invite_member/submit', methods=['POST'])
@get_callsign(Club, 'club')
@require_active_club
@special_access_required
@fresh_login_required
def invitemember(club):
    '''Allow club leader to invite member'''
    true_or_fail(club.joinmode == ClubJoinMode.BY_INVITATION,
                 'You cannot invite members when the join mode is not '
                 'by invitation.', 'invite_member')
    if form_is_valid():
        new_member = User.find_user(request.form['gradeclass'],
                                    request.form['passportname'])
        if new_member is None:
            fail('Please input correct user info to invite.', 'invite_member')
        else:
            parameters = {'club': club, 'member': new_member}
            contents = render_email_template('invitemember', parameters)
            new_member.email_user('Invitation - ' + club.name, contents)
            if new_member in club.members:
                fail('%s is already in the club.' % new_member.nickname,
                     'invite_member')
            else:
                club.send_invitation(new_member)
                flash('The invitation has been sent to %s.'
                      % new_member.nickname, 'invite_member')
    return redirect(url_for('.adjustmember', club=club.callsign))


@clubblueprint.route('/<club>/activities/', defaults={'page': 1})
@clubblueprint.route('/<club>/activities/<int:page>')
@get_callsign(Club, 'club')
def clubactivities(club, page):
    '''One Club's Activities'''
    act_num = 20
    count, acts = club.activities(limit=((page-1)*act_num, act_num))
    pagination = Pagination(page, act_num, count)
    club_pic = []
    club_pic.extend([item['upload'] for item in club.allactphotos(limit=3)[1]])
    club_pic.extend([Upload(-101) for _ in range(3 - len(club_pic))])
    return render_template('club/clubact.html',
                           club_pic=club_pic,
                           acts=acts,
                           pagination=pagination)


@clubblueprint.route('/<club>/photos/', defaults={'page': 1})
@clubblueprint.route('/<club>/photos/<int:page>')
@get_callsign(Club, 'club')
def clubphoto(club, page):
    '''Individual Club's Photo Page'''
    pic_num = 20
    count, uploads = club.allactphotos(limit=((page-1)*pic_num, pic_num))
    pagination = Pagination(page, pic_num, count)
    return render_template('club/clubphoto.html',
                           uploads=uploads,
                           pagination=pagination)


@clubblueprint.route('/<club>/new_activity')
@get_callsign(Club, 'club')
@require_active_club
@special_access_required
def newact(club):
    '''Hosting New Activity'''
    years = (lambda m: map(lambda n: m + n, range(2)))(date.today().year)
    return render_template('club/newact.html',
                           years=years)


@clubblueprint.route('/<club>/new_activity/submit', methods=['POST'])
@get_callsign(Club, 'club')
@require_active_club
@special_access_required
def newact_submit(club):
    '''Input new activity's information into database'''
    try:
        a = Activity.new()
        a.name = request.form['name']
        if not a.name:
            fail('Please enter the name of the new activity.', 'newact')
            return redirect(url_for('.newact', club=club.callsign))
        a.club = club
        a.description = FormattedText.handle(current_user, club,
                                             request.form['description'])
        a.post = FormattedText(0)
        try:
            actdate = date(int(request.form['year']),
                           int(request.form['month']),
                           int(request.form['day']))
        except ValueError:
            fail('Invalid date.', 'newact')
            return redirect(url_for('.newact', club=club.callsign))
        if actdate < date.today():
            fail('Please choose the correct date.', 'newact')
            return redirect(url_for('.newact', club=club.callsign))
        a.date = actdate
        time = ActivityTime[request.form['act_type'].upper()]
        is_other_act = time in [ActivityTime.UNKNOWN, ActivityTime.OTHERS]
        a.time = time
        a.location = request.form['location']
        time_type = request.form['time_type']
        if int(request.form['cas']) < 0 or not request.form['cas']:
            fail('Invalid CAS hours.', 'actinfo')
            return redirect(url_for('.newact', club=club.callsign))
        if time_type == 'hours':
            a.cas = int(request.form['cas'])
        else:
            a.cas = int(request.form['cas']) / 60
        if (time == ActivityTime.OTHERS or time == ActivityTime.UNKNOWN) and \
                request.form['has_selection'] == 'yes':
            choices = request.form['selections'].split(';')
            a.selections = [choice.strip() for choice in choices]
        else:
            a.selections = []
        a.create()
        flash(a.name + ' has been successfully created.', 'newact')
    except ValueError:
        fail('Please input all information to create a new activity.',
             'newact')
    else:
        for member in club.teacher_and_members:
            parameters = {'member': member, 'club': club, 'act': a,
                          'is_other_act': is_other_act}
            contents = render_email_template('newact', parameters)
            member.email_user(a.name + ' - ' + club.name, contents)
            member.notify_user(club.name + ' is going to host ' + a.name +
                               ' on ' + actdate.strftime('%b-%d-%y') + '.')
    return redirect(url_for('.newact', club=club.callsign))


@clubblueprint.route('/<club>/hongmei_status')
@get_callsign(Club, 'club')
@special_access_required
def hongmei_status(club):
    '''Check HongMei Status'''
    acts = club.activities([ActivityTime.HONGMEI], (False, True))
    return render_template('club/hmstatus.html',
                           acts=acts)


@clubblueprint.route('/<club>/hongmei_status/download')
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


@clubblueprint.route('/<club>/new_hongmei_schedule')
@get_callsign(Club, 'club')
@require_active_club
@special_access_required
def newhm(club):
    '''Input HongMei Plan'''
    acts = club.activities([ActivityTime.HONGMEI], (False, True))
    years = (lambda m: map(lambda n: m + n, range(2)))(date.today().year)
    return render_template('club/newhm.html',
                           acts=acts,
                           years=years)


@clubblueprint.route('/<club>/new_hongmei_schedule/submit', methods=['POST'])
@get_callsign(Club, 'club')
@require_active_club
@special_access_required
def newhm_submit(club):
    '''Input HongMei plan into databse'''
    contents = request.form['contents']
    try:
        actdate = date(int(request.form['year']),
                       int(request.form['month']),
                       int(request.form['day']))
    except ValueError:
        fail('Please input valid date to submit.', 'newhm')
    if contents == '' or actdate < date.today():
        fail('Please input contents or correct date to submit.', 'newhm')
    if form_is_valid():
        a = Activity.new()
        a.name = contents
        a.club = club
        a.description = FormattedText.emptytext()
        a.date = actdate
        a.time = ActivityTime.HONGMEI
        a.location = 'HongMei Elementary School'
        a.cas = 1
        a.post = FormattedText.emptytext()
        a.selections = []
        a.create()
    return redirect(url_for('.newhm', club=club.callsign))


@clubblueprint.route('/adjust_status')
@special_access_required
@require_not_student
def adjust_status():
    '''Allow admin to change club to active'''
    clubs = Club.allclubs(active_only=False)
    return render_template('club/adjuststatus.html',
                           clubs=clubs,
                           ClubJoinMode=ClubJoinMode)


@clubblueprint.route('/adjust_status/submit', methods=['POST'])
@special_access_required
@require_not_student
def adjust_status_submit():
    '''Input change in activeness into database'''
    ids = request.form.getlist('activeness')
    clubs = map(Club, ids)
    for club in clubs:
        if club.is_active:
            club.is_active = False
        else:
            club.is_active = True
    ids = request.form.getlist('joinmode')
    clubs = map(Club, ids)
    for club in clubs:
        if club.joinmode == ClubJoinMode.FREE_JOIN:
            club.joinmode = ClubJoinMode.BY_INVITATION
        elif club.joinmode == ClubJoinMode.BY_INVITATION:
            club.joinmode = ClubJoinMode.FREE_JOIN
    flash('The change in clubs\' status has been submitted.', 'adjust_status')
    return redirect(url_for('.adjust_status'))


@clubblueprint.route('/adjust_status/all_free_join', methods=['POST'])
@special_access_required
@require_not_student
def adjust_status_all_free_join():
    '''Change all clubs' join mode to free join'''
    for club in Club.allclubs(active_only=False):
        club.joinmode = ClubJoinMode.FREE_JOIN
    flash('All clubs are free to join now.', 'adjust_status')
    return redirect(url_for('.adjust_status'))


@clubblueprint.route('/adjust_status/all_by_invitation', methods=['POST'])
@special_access_required
@require_not_student
def adjust_status_all_by_invitation():
    '''Change all clubs' join mode to free join'''
    for club in Club.allclubs(active_only=False):
        club.joinmode = ClubJoinMode.BY_INVITATION
    flash('All clubs are invite-only now.', 'adjust_status')
    return redirect(url_for('.adjust_status'))


@clubblueprint.route('/<club>/register_hongmei')
@get_callsign(Club, 'club')
@login_required
@require_student_membership
@require_active_club
def registerhm(club):
    '''Register Page for HongMei Activites'''
    activities = club.activities([ActivityTime.HONGMEI], (False, True))
    acts = []
    for activity in activities:
        try:
            activity.signup_user_status(current_user)
            acts.append((activity, True))
        except NoRow:
            acts.append((activity, False))
    return render_template('club/registerhm.html',
                           acts=acts)


@clubblueprint.route('/<club>/register_hongmei/submit', methods=['POST'])
@get_callsign(Club, 'club')
@login_required
@require_student_membership
@require_active_club
def registerhm_submit(club):
    '''Submit HongMei signup info to database'''
    register = request.form.getlist('register')
    plan = ''
    for reg in register:
        act = Activity(reg)
        true_or_fail(act.club == club, 'wtf? Please enter a valid activity.',
                     'reghm')
        if form_is_valid():
            act.signup(current_user)
            plan += 'Date: ' + act.date.strftime('%b-%d-%y') + '\n\n' + \
                'Content: ' + act.name + '\n\n'
    if form_is_valid():
        parameters = {'user': current_user, 'club': club, 'plan': plan}
        contents = render_email_template('registerhm', parameters)
        current_user.email_user('HongMei Plan - ' + club.name, contents)
        flash('Your application has been successfully submitted.', 'reghm')
    return redirect(url_for('.registerhm', club=club.callsign))


@clubblueprint.route('/quit')
@fresh_login_required
def quitclub():
    '''Quit Club Page'''
    quitting_clubs = filter(lambda club: current_user != club.leader,
                            current_user.clubs)
    return render_template('club/quitclub.html',
                           quitting_clubs=quitting_clubs)


@clubblueprint.route('/quit/submit', methods=['POST'])
@fresh_login_required
def quitclub_submit():
    '''Delete connection between user and club in database'''
    club = Club(request.form['clubs'])
    if current_user == club.leader:
        fail('You cannot quit a club you lead.', 'quit')
        return redirect(url_for('.quitclub'))
    try:
        club.remove_member(current_user)
    except NoRow:
        fail('You are not a member of ' + club.name + '.', 'quit')
    else:
        reason = request.form['reason']
        parameters = {'user': current_user, 'club': club, 'reason': reason}
        contents = render_email_template('quitclub', parameters)
        club.leader.email_user('Quit Club - ' + current_user.nickname,
                               contents)
        club.leader.notify_user(current_user.nickname + ' has quit ' +
                                club.name + '.')
        flash('You have successfully quitted ' + club.name + '.', 'quit')
    return redirect(url_for('.quitclub'))


@clubblueprint.route('/info_download_all')
@special_access_required
@fresh_login_required
def allclubsinfo():
    '''Allow admin to download all clubs' info'''
    info = []
    info.append(('Club ID', 'Name', 'Leader', 'Leader\'s Class', 'Teacher',
                 'Introduction', 'Location', 'Is Active or Not', 'Type'))
    info.extend([(club.id, club.name, club.leader.passportname,
                  club.leader.grade_and_class,
                  club.teacher.email, club.intro, club.location,
                  str(club.is_active), club.type.format_name)
                 for club in Club.allclubs()])

    return download_xlsx('All Clubs\' Info.xlsx', info)


@clubblueprint.route('/new')
@fresh_login_required
def newclub():
    '''Allow student to create new club'''
    if not siteconfig.get_config('allow_club_creation'):
        abort(403)
    return render_template('club/newclub.html',
                           clubtype=ClubType)


@clubblueprint.route('/new/submit', methods=['POST'])
@fresh_login_required
def newclub_submit():
    '''Upload excel file to create new clubs'''
    if not siteconfig.get_config('allow_club_creation'):
        abort(403)
    clubname = request.form['clubname']
    email = request.form['email']
    clubtype = int(request.form['clubtype'])
    location = request.form['location']
    intro = request.form['intro']
    description = request.form['description'].strip()
    true_or_fail(clubname, 'Please input club name.', 'newclub')
    true_or_fail(email, 'Please input teacher\'s email address.', 'newclub')
    true_or_fail(location, 'Please input club\'s meeting location.', 'newclub')
    true_or_fail(intro, 'Please input club\'s one-sentence introduction.',
                        'newclub')
    true_or_fail(len(intro) <= 90, 'Your one sentence intro is too long.',
                                   'newclub')

    true_or_fail(description, 'Please input club\'s paragraph description.',
                              'newclub')
    if form_is_valid():
        c = Club.new()
        c.name = clubname
        teacher = User.find_teacher(email)
        if teacher is not None:
            c.teacher = teacher
        else:
            fail('There is no teacher with this email address.', 'newclub')
            return redirect(url_for('.newclub'))
        c.leader = current_user
        c.description = FormattedText.emptytext()
        c.location = location
        c.is_active = False
        c.intro = intro
        c.picture = Upload(-101)
        c.type = ClubType(clubtype)
        c.joinmode = ClubJoinMode.FREE_JOIN
        c.create()
        c.add_member(current_user)
        c.description = FormattedText.handle(current_user, c,
                                             request.form['description'])
        return redirect(url_for('.clubintro', club=c.callsign))
    return redirect(url_for('.newclub'))


@clubblueprint.route('/management_list/', defaults={'page': 1})
@clubblueprint.route('/management_list/<int:page>')
@special_access_required
@fresh_login_required
def clubmanagementlist(page):
    '''Allow admin to access club management list'''
    num = 20
    count, clubs = Club.allclubs(limit=((page-1)*num, num))
    pagination = Pagination(page, num, count)
    return render_template('club/clubmanagementlist.html',
                           clubs=clubs,
                           pagination=pagination)


@clubblueprint.route('/adjust_excellent_clubs')
@special_access_required
@fresh_login_required
def adjustclubs():
    '''Allow admin to change clubs' status'''
    clubs = Club.allclubs()
    return render_template('club/adjustclubs.html',
                           clubs=clubs)


@clubblueprint.route('/adjust_excellent_clubs/submit', methods=['POST'])
@special_access_required
@fresh_login_required
def adjustclubs_submit():
    '''Input change in clubs into database'''
    exc_clubs = Club.excellentclubs()
    club = Club(request.form['clubid'])
    if club in exc_clubs:
        exc_clubs.remove(club)
    else:
        exc_clubs.append(club)
    Club.set_excellentclubs(exc_clubs)
    flash('The change has been successfully submitted', 'adjustclubs')
    return redirect(url_for('.adjustclubs'))
