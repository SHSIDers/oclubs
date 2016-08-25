#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

from datetime import date, timedelta, datetime

from flask import (
    Blueprint, render_template, url_for, request, redirect, abort, flash,
    jsonify
)
from flask_login import current_user, login_required, fresh_login_required

from oclubs.objs import User, Club, Activity, Upload, FormattedText
from oclubs.enums import UserType, ClubType, ActivityTime, ClubJoinMode
from oclubs.shared import (
    get_callsign, special_access_required, download_xlsx, read_xlsx,
    render_email_template, Pagination
)
from oclubs.exceptions import PasswordTooShort, NoRow

userblueprint = Blueprint('userblueprint', __name__)


@userblueprint.route('/quit_club')
@fresh_login_required
def quitclub():
    '''Quit Club Page'''
    quitting_clubs = []
    for club in current_user.clubs:
        if club not in Club.get_clubs_special_access(current_user):
            quitting_clubs.append(club)
    return render_template('user/quitclub.html',
                           quitting_clubs=quitting_clubs)


@userblueprint.route('/quit_club/submit', methods=['POST'])
@fresh_login_required
def quitclub_submit():
    '''Delete connection between user and club in database'''
    club = Club(request.form['clubs'])
    club.remove_member(current_user)
    reason = request.form['reason']
    parameters = {'user': current_user, 'club': club, 'reason': reason}
    contents = render_email_template('quitclub', parameters)
    club.leader.email_user('Quit Club - ' + current_user.nickname, contents)
    club.leader.notify_user(current_user.nickname + ' has quit ' +
                            club.name + '.')
    flash('You have successfully quitted ' + club.name + '.', 'quit')
    return redirect(url_for('.quitclub'))


@userblueprint.route('/')
@login_required
def personal():
    '''Student Personal Page'''
    pictures = [Upload(-num) for num in range(1, 21)]
    if current_user.type == UserType.STUDENT:
        clubs = current_user.clubs
        castotal = sum(current_user.cas_in_club(club)
                       for club in current_user.clubs)
        meetings_obj = current_user.activities_reminder(
            [ActivityTime.NOON, ActivityTime.AFTERSCHOOL])
        meetings = []
        meetings.extend([meeting for meeting in meetings_obj])
        acts_obj = current_user.activities_reminder([ActivityTime.UNKNOWN,
                                                     ActivityTime.HONGMEI,
                                                     ActivityTime.OTHERS])
        activities = []
        activities.extend([act for act in acts_obj])
        leader_club = filter(lambda club_obj: current_user == club_obj.leader,
                             clubs)
        return render_template('user/student.html',
                               pictures=pictures,
                               clubs=clubs,
                               castotal=castotal,
                               meetings=meetings,
                               activities=activities,
                               leader_club=leader_club)
    elif current_user.type == UserType.TEACHER:
        myclubs = Club.get_clubs_special_access(current_user)
        return render_template('user/teacher.html',
                               pictures=pictures,
                               myclubs=myclubs,
                               UserType=UserType)
    else:
        years = [(date.today() + timedelta(days=365*diff)).year
                 for diff in range(2)]
        return render_template('user/admin.html',
                               pictures=pictures,
                               years=years)


@userblueprint.route('/submit_info', methods=['POST'])
@login_required
def personalsubmitinfo():
    '''Change user's information in database'''
    if request.form['name'] != '':
        current_user.nickname = request.form['name']
    if request.form['email'] != '':
        current_user.email = request.form['email']
    if request.form['phone'] != '':
        current_user.phone = request.form['phone']
    if request.form['picture'] is not None:
        current_user.picture = Upload(request.form['picture'])
    flash('Your information has been successfully changed.', 'status_info')
    return redirect(url_for('.personal'))


@userblueprint.route('/submit_password', methods=['POST'])
@login_required
def personalsubmitpassword():
    '''Change user's password in database'''
    user_login = User.attempt_login(current_user.studentid,
                                    request.form['old'])
    if user_login is not None:
        if request.form['new'] == '':
            flash('Please enter new password.', 'status_pw')
        elif request.form['new'] == request.form['again']:
            try:
                current_user.password = request.form['new']
                flash('Your information has been successfully changed.',
                      'status_pw')
            except PasswordTooShort:
                flash('Password must be at least six digits.', 'status_pw')
        else:
            flash('You have entered two different passwords. '
                  'Please enter again.', 'status_pw')
    else:
        flash('You have entered wrong old password. Please enter again.',
              'status_pw')
    return redirect(url_for('.personal'))


@userblueprint.route('/<club>/switch_mode/submit', methods=['POST'])
@get_callsign(Club, 'club')
@special_access_required
def switchmode(club):
    '''Allow club teacher to switch club's mode'''
    if club.joinmode == ClubJoinMode.FREE_JOIN:
        club.joinmode = ClubJoinMode.BY_INVITATION
    elif club.joinmode == ClubJoinMode.BY_INVITATION:
        club.joinmode = ClubJoinMode.FREE_JOIN
    flash(club.name + '\'s mode has been successfully changed.', 'joinmode')
    return redirect(url_for('.personal'))


@userblueprint.route('/<club>/to_active/submit', methods=['POST'])
@get_callsign(Club, 'club')
@special_access_required
def toactive(club):
    '''Allow club teacher to change club to active'''
    club.is_active = True
    flash(club.name + ' is active now.', 'is_active')
    return redirect(url_for('.personal'))


@userblueprint.route('/all_clubs_info')
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


@userblueprint.route('/all_activities_info')
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


@userblueprint.route('/all_users_info')
@special_access_required
@fresh_login_required
def allusersinfo():
    '''Allow admin to download all users' info'''
    info = []
    info.append(('ID', 'Student ID', 'Nick Name', 'Passport Name', 'Email',
                 'Phone'))
    info.extend([(user.id, user.studentid, user.nickname, user.passportname,
                  user.email, str(user.phone)) for user in User.allusers()])

    return download_xlsx('All Users\' Info.xlsx', info)


@userblueprint.route('/new_teachers')
@special_access_required
@fresh_login_required
def newteachers():
    '''Allow admin to create new user or clubs'''
    return render_template('user/newteachers.html')


@userblueprint.route('/new_teachers/submit', methods=['POST'])
@special_access_required
@fresh_login_required
def newteachers_submit():
    '''Create new teacher accounts with xlsx'''
    if request.files['excel'].filename == '':
        raise ValueError
    try:
        contents = read_xlsx(request.files['excel'], 'Teachers',
                             ['ID', 'Official Name', 'Email Address'])
    except KeyError:
        flash('Please change sheet name to "Teachers"', 'newteachers')
        return redirect(url_for('.newteachers'))
    except ValueError:
        flash('Please input in the correct order.', 'newteachers')
        return redirect(url_for('.newteachers'))
    # except BadZipfile:
    #     flash('Please upload an excel file.', 'newteachers')
    #     return redirect(url_for('.newteachers'))

    from oclubs.worker import handle_teacher_xlsx
    for each in contents:
        handle_teacher_xlsx.delay(*each)

    flash('New teacher accounts have been successfully created. '
          'Their passwords have been sent to their accounts.', 'newteachers')
    return redirect(url_for('.newteachers'))


@userblueprint.route('/refresh_users/submit', methods=['POST'])
@special_access_required
@fresh_login_required
def refreshusers_submit():
    '''Upload excel file to create new users'''
    from oclubs.worker import refresh_user
    refresh_user.delay()
    flash('Student accounts\' information has been successfully refreshed.',
          'refresh_users')
    return redirect(url_for('.personal'))


@userblueprint.route('/rebuild_elastic_search/submit', methods=['POST'])
@special_access_required
@fresh_login_required
def rebuildsearch_submit():
    '''Rebuild elastic search engine to fix asyncronized situation'''
    from oclubs.worker import rebuild_elasticsearch
    rebuild_elasticsearch.delay()
    flash('Search engine has been fixed.', 'rebuild_search')
    return redirect(url_for('.personal'))


@userblueprint.route('/download_new_passwords')
@special_access_required
@fresh_login_required
def download_new_passwords():
    '''Allow admin to download new accounts' passwords'''
    result = []
    result.append(['Passport Name', 'Login Name', 'Password'])
    users = User.get_new_passwords()
    result.extend([(user.passportname,
                    user.studentid,
                    password) for user, password in users])
    return download_xlsx('New Accounts\' Passwords.xlsx', result)


@userblueprint.route('/disable_accounts')
@special_access_required
@fresh_login_required
def disableaccounts():
    '''Allow admin to disable any account'''
    users = User.allusers()
    return render_template('user/disableaccounts.html',
                           users=users)


@userblueprint.route('/disable_accounts/submit', methods=['POST'])
@special_access_required
@fresh_login_required
def disableaccounts_submit():
    '''Input disabling information into database'''
    user = User(request.form['id'])
    user.password = None
    flash(user.passportname + ' has been successfully disabled.',
          'disableaccounts')
    return redirect(url_for('.disableaccounts'))


@userblueprint.route('/new_club')
@fresh_login_required
def newclub():
    '''Allow teacher or admin to create new club'''
    if current_user.type == UserType.STUDENT:
        abort(403)
    return render_template('user/newclub.html',
                           clubtype=ClubType)


@userblueprint.route('/new_club/submit', methods=['POST'])
@fresh_login_required
def newclub_submit():
    '''Upload excel file to create new clubs'''
    if current_user.type == UserType.STUDENT:
        abort(403)
    clubname = request.form['clubname']
    studentid = request.form['studentid']
    passportname = request.form['passportname']
    clubtype = int(request.form['clubtype'])
    leader = User.find_user(studentid, passportname)
    if leader is None:
        flash('Please input correct student info.', 'newclub')
    elif clubname == '':
        flash('Please input club name.', 'newclub')
    else:
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


@userblueprint.route('/club_management_list/', defaults={'page': 1})
@userblueprint.route('/club_management_list/<int:page>')
@special_access_required
@fresh_login_required
def clubmanagementlist(page):
    '''Allow admin to access club management list'''
    num = 20
    count, clubs = Club.allclubs(limit=((page-1)*num, num))
    pagination = Pagination(page, num, count)
    return render_template('user/clubmanagementlist.html',
                           clubs=clubs,
                           pagination=pagination)


@userblueprint.route('/adjust_clubs')
@special_access_required
@fresh_login_required
def adjustclubs():
    '''Allow admin to change clubs' status'''
    clubs = Club.allclubs()
    return render_template('user/adjustclubs.html',
                           clubs=clubs)


@userblueprint.route('/adjust_clubs/submit', methods=['POST'])
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


@userblueprint.route('/change_password')
@special_access_required
@fresh_login_required
def changepassword():
    '''Allow admin to change users' password'''
    users = User.allusers()
    return render_template('user/changepassword.html',
                           users=users)


@userblueprint.route('/change_password/submit', methods=['POST'])
@special_access_required
@fresh_login_required
def changepassword_submit():
    '''Input new password into database'''
    password = request.form['password']
    if password == '':
        flash('Please input valid password.', 'password')
        return redirect(url_for('.changepassword'))
    user = User(request.form['id'])
    try:
        user.password = password
    except PasswordTooShort:
        flash('Password must be at least six digits.', 'password')
        return redirect(url_for('.changepassword'))
    flash(user.nickname + '\'s password has been successfully set to ' +
          password + '.', 'password')
    return redirect(url_for('.changepassword'))


@userblueprint.route('/forgot_password')
def forgotpw():
    '''Page for retrieving password'''
    return render_template('user/forgotpassword.html')


@userblueprint.route('/change_user_info')
@special_access_required
@fresh_login_required
def changeuserinfo():
    '''Allow admin to change users' information'''
    users = User.allusers()
    return render_template('user/changeuserinfo.html',
                           users=users)


@userblueprint.route('/change_user_info/submit', methods=['POST'])
@special_access_required
@fresh_login_required
def changeuserinfo_submit():
    '''Input change of info into database'''
    property_type = request.form['type']
    content = request.form['content'].strip()
    userid = request.form['userid']
    if content == '-':
        content = None
    else:
        try:
            content = int(content)
        except ValueError:
            pass

    try:
        setattr(User(userid), property_type, content)
    except Exception as e:
        status = type(e).__name__
    else:
        status = 'success'
    return jsonify({'result': status})


@userblueprint.route('/check_hongmei_schedule/download', methods=['POST'])
@special_access_required
def checkhongmeischedule_download():
    '''Allow admin to check HongMei schedule'''
    info = []
    try:
        date = datetime.strptime(request.form['year'] +
                                 request.form['month'] +
                                 request.form['day'], '%Y%m%d')
    except ValueError:
        flash('You have input wrong date for HongMei schedule.', 'status_info')
        return redirect(url_for('.personal'))
    info.append((date.strftime('%b-%d-%Y'),))
    info.append(('Club Name', 'Members'))
    for act in Activity.get_activities_conditions(
                    times=(ActivityTime.HONGMEI,),
                    dates=date
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


@userblueprint.route('/<club>/register_hongmei')
@get_callsign(Club, 'club')
@login_required
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
    return render_template('user/registerhm.html',
                           acts=acts)


@userblueprint.route('/<club>/register_hongmei/submit', methods=['POST'])
@get_callsign(Club, 'club')
@login_required
def registerhm_submit(club):
    '''Submit HongMei signup info to database'''
    register = request.form.getlist('register')
    plan = ''
    for reg in register:
        act = Activity(reg)
        act.signup(current_user)
        plan += 'Date: ' + act.date.strftime('%b-%d-%y') + '\n\n' + \
            'Content: ' + act.name + '\n\n'
    parameters = {'user': current_user, 'club': club, 'plan': plan}
    contents = render_email_template('registerhm', parameters)
    current_user.email_user('HongMei Plan - ' + club.name, contents)
    flash('Your application has been successfully submitted.', 'reghm')
    return redirect(url_for('.registerhm', club=club.callsign))


@userblueprint.route('/notifications/', defaults={'page': 1})
@userblueprint.route('/notifications/<int:page>')
@login_required
def notifications(page):
    '''Allow users to check their notifications'''
    note_num = 20
    notes_all = current_user.get_notifications(
        limit=((page-1)*note_num, note_num)
    )
    current_user.set_notifications_readall()
    invitations_all = current_user.get_invitation()
    return render_template('user/notifications.html',
                           notifications=notes_all[1],
                           number=current_user.get_unread_notifications_num(),
                           pagination=Pagination(page, note_num, notes_all[0]),
                           invitations=invitations_all)


@userblueprint.route('/notifications/submit', methods=['POST'])
@login_required
def invitation_reply():
    reply = request.form['reply']
    club = Club(request.form['club'])
    invitations = current_user.get_invitation()
    isinvited = False
    for invitation in invitations:
        if invitation['club'] == club:
            isinvited = True
            break
    if not isinvited:
        abort(403)
    if reply == "accept":
        club.add_member(current_user)
        flash('You have successfully joined %s.' % club.name, 'reply')
    elif reply == "decline":
        flash('You have declined the invitation of %s.' % club.name, 'reply')
    current_user.delete_invitation(club)
    return redirect(url_for('.notifications'))
