#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

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

clubblueprint = Blueprint('clubblueprint', __name__)


@clubblueprint.route('/list/<club_type>')
def clublist(club_type):
    '''Club list by club type'''
    num = 18
    if club_type == 'all':
        clubs = Club.randomclubs(num)
    elif club_type == 'excellent':
        clubs = Club.excellentclubs()
    else:
        try:
            typ = ClubType[club_type.upper()]
        except KeyError:
            abort(404)
        else:
            clubs = Club.randomclubs(num, [typ])
    return render_template('club/clublist.html',
                           is_list=True,
                           clubs=clubs,
                           club_type=club_type)


@clubblueprint.route('/<club>/manage')
@get_callsign(Club, 'club')
@require_active_club
@special_access_required
def club(club):
    '''Club Management Page'''
    return render_template('club/clubmanage.html')


@clubblueprint.route('/<club>/')
def clubredirect(club):
    return redirect(url_for('.clubintro', club=club))


@clubblueprint.route('/<club>/introduction')
@get_callsign(Club, 'club')
def clubintro(club):
    '''Club Intro'''
    free_join = (current_user.is_active and
                 club.joinmode == ClubJoinMode.FREE_JOIN and
                 current_user.type == UserType.STUDENT and
                 current_user not in club.members)

    return render_template('club/clubintro.html',
                           free_join=free_join)


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
            fail('You are already in %s.' % club.name)
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
    for member in club.members:
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
    has_access = (current_user.id == club.leader.id or
                  current_user.id == club.teacher.id or
                  current_user.type == UserType.ADMIN)
    return render_template('club/memberinfo.html',
                           has_access=has_access)


@clubblueprint.route('/<club>/member_info/download')
@get_callsign(Club, 'club')
@require_membership
@special_access_required
def memberinfo_download(club):
    '''Download members' info'''
    info = []
    info.append(('Nick Name', 'Student ID', 'Passport Name', 'Email'))
    info.extend([(member.nickname, member.studentid, member.passportname,
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
    if request.form['intro'] != '':
        club.intro = request.form['intro']

    desc = request.form['description'].strip()
    if desc != club.description:
        club.description = FormattedText.handle(current_user, club,
                                                request.form['description'])
    if request.files['picture'].filename != '':
        try:
            club.picture = Upload.handle(current_user, club,
                                         request.files['picture'])
        except UploadNotSupported:
            fail('Please upload the correct file type.', 'clubinfo')
            return redirect(url_for('.changeclubinfo', club=club.callsign))
    for member in club.members:
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
    member = User(request.form['studentid'])
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
        new_member = User.find_user(request.form['studentid'],
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
            fail('Please enter the name of the new activity.')
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
            a.selections = [choice.strip() for choice in choices]
        else:
            a.selections = []
        a.create()
        flash(a.name + ' has been successfully created.', 'newact')
    except ValueError:
        fail('Please input all information to create a new activity.',
             'newact')
    else:
        for member in club.members:
            parameters = {'member': member, 'club': club, 'act': a}
            contents = render_email_template('newact', parameters)
            member.email_user(a.name + ' - ' + club.name, contents)
            member.notify_user(club.name + ' is going to host ' + a.name +
                               ' on ' + date.strftime('%b-%d-%y') + '.')
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


@clubblueprint.route('/<club>/switch_mode/submit', methods=['POST'])
@get_callsign(Club, 'club')
@require_active_club
@special_access_required
@require_not_student
def switchmode(club):
    '''Allow club teacher to switch club's mode'''
    if club.joinmode == ClubJoinMode.FREE_JOIN:
        club.joinmode = ClubJoinMode.BY_INVITATION
    elif club.joinmode == ClubJoinMode.BY_INVITATION:
        club.joinmode = ClubJoinMode.FREE_JOIN
    flash(club.name + '\'s mode has been successfully changed.', 'joinmode')
    return redirect(url_for('userblueprint.personal'))


@clubblueprint.route('/<club>/to_active/submit', methods=['POST'])
@get_callsign(Club, 'club')
@special_access_required
@require_not_student
def toactive(club):
    '''Allow club teacher to change club to active'''
    club.is_active = True
    flash(club.name + ' is active now.', 'is_active')
    return redirect(url_for('userblueprint.personal'))


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
    info.append(('Club ID', 'Name', 'Leader', 'Teacher', 'Introduction',
                 'Location', 'Is Active or Not', 'Type'))
    info.extend([(club.id, club.name, club.leader.passportname,
                  club.teacher.passportname, club.intro, club.location,
                  str(club.is_active), club.type.format_name)
                 for club in Club.allclubs()])

    return download_xlsx('All Clubs\' Info.xlsx', info)


@clubblueprint.route('/new')
@fresh_login_required
@require_not_student
def newclub():
    '''Allow teacher or admin to create new club'''
    return render_template('club/newclub.html',
                           clubtype=ClubType)


@clubblueprint.route('/new/submit', methods=['POST'])
@fresh_login_required
@require_not_student
def newclub_submit():
    '''Upload excel file to create new clubs'''
    clubname = request.form['clubname']
    studentid = request.form['studentid']
    passportname = request.form['passportname']
    clubtype = int(request.form['clubtype'])
    leader = User.find_user(studentid, passportname)
    true_or_fail(leader is not None, 'Please input correct student info.',
                 'newclub')
    true_or_fail(clubname, 'Please input club name.', 'newclub')

    if form_is_valid():
        c = Club.new()
        c.name = clubname
        c.teacher = current_user
        c.leader = leader
        c.description = FormattedText.emptytext()
        c.location = ''
        c.is_active = True
        c.intro = ''
        c.picture = Upload(-101)
        c.type = ClubType(clubtype)
        c.joinmode = ClubJoinMode.FREE_JOIN
        c.create()
        c.add_member(leader)
        flash(c.name + ' has been successfully created.', 'newclub')
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
