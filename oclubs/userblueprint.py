#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals
import traceback

from flask import (
    Blueprint, render_template, url_for, request, session, redirect, abort, flash, jsonify
)
from flask_login import current_user, login_required, fresh_login_required

from oclubs.objs import User, Club, Activity, Upload
from oclubs.enums import UserType, ClubType, ActivityTime
from oclubs.shared import get_callsign, special_access_required, download_xlsx, read_xlsx, render_email_template

userblueprint = Blueprint('userblueprint', __name__)


@userblueprint.route('/quit_club')
@login_required
def quitclub():
    '''Quit Club Page'''
    clubs_obj = current_user.clubs
    clubs = []
    for club_obj in clubs_obj:
        club = {}
        club['id'] = club_obj.id
        club['name'] = club_obj.name
        clubs.append(club)
    return render_template('user/quitclub.html',
                           title='Quit Club',
                           clubs=clubs)


@userblueprint.route('/quit_club/submit', methods=['POST'])
@login_required
def quitclub_submit():
    '''Delete connection between user and club in database'''
    club = Club(request.form['clubs'])
    club.remove_member(current_user)
    reason = request.form['reason']
    parameters = {'user': current_user, 'club': club, 'reason': reason}
    contents = render_email_template('quitclub', parameters)
    # club.leader.email_user('Quit Club - ' + current_user.nickname, contents)
    flash('You have successfully quitted ' + club.name + '.', 'quit')
    return redirect(url_for('.quitclub'))


@userblueprint.route('/')
@login_required
def personal():
    '''Student Personal Page'''
    pictures = []
    for num in range(1, 21):
        pictures.append(Upload(-num))
    if current_user.type == UserType.STUDENT:
        clubs = current_user.clubs
        castotal = 0
        cas_clubs = []
        for club in clubs:
            cas_clubs.append(current_user.cas_in_club(club))
        for cas in cas_clubs:
            castotal += cas
        meetings_obj = current_user.activities_reminder([ActivityTime.NOON, ActivityTime.AFTERSCHOOL])
        meetings = []
        for meeting_obj in meetings_obj:
            meeting = {}
            meeting['act'] = meeting_obj
            time_int = meeting_obj.time
            if time_int == ActivityTime.NOON:
                time = "Noon"
            else:
                time = "Afternoon"
            meeting['time'] = meeting_obj.date.strftime('%Y-%m-%d') + ": " + time
            meetings.append(meeting)
        activities_obj = current_user.activities_reminder([ActivityTime.UNKNOWN,
                                                           ActivityTime.HONGMEI,
                                                           ActivityTime.OTHERS])
        activities = []
        for act_obj in activities_obj:
            act = {}
            act['act'] = act_obj
            time_int = act_obj.time
            if time_int == ActivityTime.UNKNOWN:
                time = "Unknown time"
            elif time_int == ActivityTime.HONGMEI:
                time = "HongMei activity"
            else:
                time = "Individual club activity"
            act['time'] = str(act_obj.date) + ": " + time
            activities.append(act)
        leader_club = []
        for club_obj in clubs:
            if current_user == club_obj.leader:
                leader_club.append(club_obj)
        return render_template('user/student.html',
                               title=current_user.nickname,
                               pictures=pictures,
                               clubs=clubs,
                               castotal=castotal,
                               meetings=meetings,
                               activities=activities,
                               leader_club=leader_club)
    elif current_user.type == UserType.TEACHER:
        myclubs = Club.get_clubs_special_access(current_user)
        return render_template('user/teacher.html',
                               title=current_user.nickname,
                               pictures=pictures,
                               myclubs=myclubs,
                               UserType=UserType)
    else:
        return render_template('user/admin.html',
                               title=current_user.nickname,
                               pictures=pictures)


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
@login_required  # FIXME: fresh_login_required
def personalsubmitpassword():
    '''Change user's password in database'''
    user_login = User.attempt_login(current_user.studentid, request.form['old'])
    if user_login is not None:
        if request.form['new'] == request.form['again']:
            current_user.password = request.form['new']
            flash('Your information has been successfully changed.', 'status_pw')
        else:
            flash('You have entered two different passwords. Please enter again.', 'status_pw')
    else:
        flash('You have entered wrong old password. Please enter again.', 'status_pw')
    return redirect(url_for('.personal'))


@userblueprint.route('/all_clubs_info')
@special_access_required
def allclubsinfo():
    '''Allow admin to download all clubs' info'''
    info = []
    info.append(['Club ID', 'Name', 'Leader', 'Teacher', 'Introduction', 'Location', 'Is Active or Not', 'Type'])
    clubs = Club.allclubs()
    for club in clubs:
        info_each = []
        info_each.append(club.id)
        info_each.append(club.name)
        info_each.append(club.leader.passportname)
        info_each.append(club.teacher.passportname)
        info_each.append(club.intro)
        info_each.append(club.location)
        info_each.append(str(club.is_active))
        info_each.append(club.type.format_name)
        info.append(info_each)
    return download_xlsx('All Clubs\' Info.xlsx', info)


@userblueprint.route('/all_activities_info')
@special_access_required
def allactivitiesinfo():
    '''Allow admin to download all activities' info'''
    info = []
    info.append(['Activity ID', 'Name', 'Club', 'Date', 'Time (Type)', 'Location', 'CAS Hours'])
    acts = Activity.all_activities()
    for act in acts:
        info_each = []
        info_each.append(act.id)
        info_each.append(act.name)
        info_each.append(act.club.name)
        info_each.append(act.date.strftime('%b-%d-%y'))
        info_each.append(act.time.format_name)
        info_each.append(act.location)
        info_each.append(act.cas)
        info.append(info_each)
    return download_xlsx('All Activities\' Info.xlsx', info)


@userblueprint.route('/all_users_info')
@special_access_required
def allusersinfo():
    '''Allow admin to download all users' info'''
    info = []
    info.append(['ID', 'Student ID', 'Nick Name', 'Passport Name', 'Email', 'Phone'])
    users = User.allusers()
    for user in users:
        info_each = []
        info_each.append(user.id)
        info_each.append(user.studentid)
        info_each.append(user.nickname)
        info_each.append(user.passportname)
        info_each.append(user.email)
        info_each.append(str(user.phone))
        info.append(info_each)
    return download_xlsx('All Users\' Info.xlsx', info)


# @userblueprint.route('/new_users')
# @login_required
# @special_access_required
# def newusers():
#     '''Allow admin to create new user or clubs'''
#     return render_template('user/newusers.html',
#                            title='New Users')


@userblueprint.route('/refresh_users/submit', methods=['POST'])
@special_access_required
def refreshusers_submit():
    '''Upload excel file to create new users'''
    # if request.files['excel'].filename == '':
    #     raise ValueError
    # try:
    #     contents = read_xlsx(request.files['excel'], 'Users')
    # except KeyError:
    #     flash('Please change sheet name to "Users"', 'newusers')
    #     return redirect(url_for('.new'))

    from oclubs.worker import refresh_user
    refresh_user.delay()
    flash('Student accounts\' information has been successfully refreshed', 'refresh_users')
    return redirect(url_for('.peronsal'))


@userblueprint.route('/new_club')
@login_required
def newclub():
    '''Allow teacher or admin to create new club'''
    if current_user.type == UserType.STUDENT:
        abort(403)
    return render_template('user/newclub.html',
                           title='New Club')


@userblueprint.route('/new_club/submit', methods=['POST'])
@special_access_required
def newclub_submit():
    '''Upload excel file to create new clubs'''
    pass


@userblueprint.route('/club_management_list')
@special_access_required
def clubmanagementlist():
    '''Allow admin to access club management list'''
    clubs = Club.allclubs()
    return render_template('user/clubmanagementlist.html',
                           title='Club Management List',
                           clubs=clubs)


@userblueprint.route('/adjust_clubs')
@special_access_required
def adjustclubs():
    '''Allow admin to change clubs' status'''
    clubs = Club.allclubs()
    return render_template('user/adjustclubs.html',
                           title='Adjust Clubs',
                           clubs=clubs)


@userblueprint.route('/adjust_clubs/submit', methods=['POST'])
@special_access_required
def adjustclubs_submit():
    '''Input change in clubs into database'''
    exc_clubs = Club.excellentclubs()
    print exc_clubs
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
def changepassword():
    '''Allow admin to change users' password'''
    users = User.allusers()
    return render_template('user/changepassword.html',
                           title='Change Password',
                           users=users)


@userblueprint.route('/change_password/submit', methods=['POST'])
@special_access_required
def changepassword_submit():
    '''Input new password into database'''
    password = request.form['password']
    if password == '':
        flash('Please input valid password.', 'password')
        return redirect(url_for('.changepassword'))
    user = User(request.form['id'])
    user.password = password
    flash(user.nickname + '\'s password has been successfully set to ' + password + '.', 'password')
    return redirect(url_for('.changepassword'))


@userblueprint.route('/forgot_password')
def forgotpw():
    '''Page for retrieving password'''
    return render_template('user/forgotpassword.html',
                           title='Forgot Password')


@userblueprint.route('/change_user_info')
@special_access_required
def changeuserinfo():
    '''Allow admin to change users' information'''
    users = User.allusers()
    return render_template('user/changeuserinfo.html',
                           title='Change Users\' Info',
                           users=users)


@userblueprint.route('/change_user_info/submit', methods=['POST'])
@special_access_required
def changeuserinfo_submit():
    '''Input change of info into database'''
    property_type = request.form['type']
    content = request.form['content']
    userid = request.form['userid']
    try:
        setattr(User(userid), property_type, content)
    except Exception as e:
        status = type(e).__name__
        traceback.print_exc()
    else:
        status = 'success'
    return jsonify({'result': status})


@userblueprint.route('/<club>/register_hongmei')
@get_callsign(Club, 'club')
@login_required
def registerhm(club):
    '''Register Page for HongMei Activites'''
    acts = club.activities([ActivityTime.HONGMEI], (False, True))
    return render_template('user/registerhm.html',
                           title='Register for HongMei',
                           club=club.name,
                           acts=acts)


@userblueprint.route('/<club>/register_hongmei/submit', methods=['POST'])
@get_callsign(Club, 'club')
@login_required
def registerhm_submit(club):
    '''Submit HongMei signup info to database'''
    register = request.form['register']
    plan = ''
    for reg in register:
        act = Activity(reg)
        act.signup(current_user)
        plan += 'Date: ' + act.date.strftime('%b-%d-%y') + '\n\n' + \
            'Content: ' + act.name + '\n\n'
    parameters = {'user': current_user, 'club': club, 'plan': plan}
    contents = render_email_template('registerhm', parameters)
    # current_user.email_user('HongMei Plan - ' + club.name, contents)
    flash('Your application has been successfully submitted.', 'reghm')
    return redirect(url_for('.registerhm', club=club.callsign))
