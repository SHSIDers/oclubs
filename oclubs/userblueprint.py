#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

from flask import (
    Blueprint, render_template, url_for, request, session, redirect, abort, flash
)
from flask_login import current_user, login_required, fresh_login_required

from oclubs.objs import User, Club, Upload
from oclubs.enums import UserType, ClubType, ActivityTime

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
    return render_template('quitclub.html',
                           title='Quit Club',
                           clubs=clubs)


@userblueprint.route('/quit_club/submit', methods=['POST'])
@login_required
def quitclub_submit():
    '''Delete connection between user and club in database'''
    club = Club(request.form['clubs'])
    club.remove_member(current_user)
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
            meeting['club'] = meeting_obj.club
            time_int = meeting_obj.time
            if time_int == ActivityTime.NOON:
                time = "Noon"
            else:
                time = "Afternoon"
            meeting['time'] = meeting_obj.date + ": " + time
            meeting['location'] = meeting_obj.location
            meetings.append(meeting)
        activities_obj = current_user.activities_reminder([ActivityTime.UNKNOWN,
                                                           ActivityTime.HONGMEI,
                                                           ActivityTime.OTHERS])
        activities = []
        for act_obj in activities_obj:
            act = {}
            act['club'] = act_obj.club
            time_int = act_obj.time
            if time_int == ActivityTime.UNKNOWN:
                time = "Unknown time"
            elif time_int == ActivityTime.HONGMEI:
                time = "HongMei activity"
            else:
                time = "Individual club activity"
            act['time'] = str(act_obj.date) + ": " + time
            act['location'] = act_obj.location
            activities.append(act)
        leader_club = []
        for club_obj in clubs:
            if current_user == club_obj.leader:
                leader_club.append(club_obj)
        return render_template('student.html',
                               title=current_user.nickname,
                               pictures=pictures,
                               clubs=clubs,
                               castotal=castotal,
                               meetings=meetings,
                               activities=activities,
                               leader_club=leader_club,
                               UserType=UserType)
    else:
        myclubs = Club.get_clubs_special_access(current_user)
        return render_template('teacher.html',
                               title=current_user.nickname,
                               pictures=pictures,
                               myclubs=myclubs,
                               UserType=UserType)


@userblueprint.route('/submit_info', methods=['POST'])
@login_required
def personal_submit_info():
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
def personal_submit_password():
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


@userblueprint.route('/forgot_password')
def forgotpw():
    '''Page for retrieving password'''
    return render_template('forgotpassword.html',
                           title='Retrieve Password')


@userblueprint.route('/forgot_password/submit', methods=['POST'])
def forgotpw_submit():
    # TODO: accept input  to retrieve password
    pass
