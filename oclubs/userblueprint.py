#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

from flask import (
    Blueprint, render_template, url_for, request, session, redirect, abort, flash
)

import oclubs
from oclubs.enums import UserType, ClubType, ActivityTime

userblueprint = Blueprint('userblueprint', __name__)


@userblueprint.route('/quit_club')
def quitclub():
    '''Quit Club Page'''
    if 'user_id' not in session:
        abort(401)
    user_obj = oclubs.objs.User(session['user_id'])
    clubs_obj = user_obj.clubs
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
def quitclub_submit():
    '''Delete connection between user and club in database'''
    club = oclubs.objs.Club(request.form['clubs'])
    user_obj = oclubs.objs.User(session['user_id'])
    club.remove_member(user_obj)
    flash('You have successfully quitted ' + request.form['clubs'], 'quit')
    return redirect(url_for('.quitclub'))


@userblueprint.route('/')
def personal():
    '''Student Personal Page'''
    if 'user_id' not in session:
        abort(401)
    user_obj = oclubs.objs.User(session['user_id'])
    pictures = []
    for num in range(1, 21):
        pictures.append(oclubs.objs.Upload(-num))
    if user_obj.type == UserType.STUDENT:
        clubs = user_obj.clubs
        castotal = 0
        cas_clubs = []
        # for club in clubs:
        #     cas_clubs.append(user_obj.cas_in_club(club))
        # for cas in cas_clubs:
        #     castotal += cas
        meetings_obj = user_obj.activities_reminder([ActivityTime.NOON, ActivityTime.AFTERSCHOOL])
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
        activities_obj = user_obj.activities_reminder([ActivityTime.UNKNOWN,
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
            act['time'] = act_obj.date + ": " + time
            act['location'] = act_obj.location
            activities.append(act)
        leader_club = []
        for club_obj in clubs:
            if user_obj == club_obj.leader:
                leader_club.append(club_obj)
        return render_template('student.html',
                               title=user_obj.nickname,
                               pictures=pictures,
                               user_obj=user_obj,
                               clubs=clubs,
                               castotal=castotal,
                               meetings=meetings,
                               activities=activities,
                               leader_club=leader_club,
                               UserType=UserType)
    else:
        myclubs = oclubs.objs.Club.get_clubs_special_access(user_obj)
        return render_template('teacher.html',
                               title=user_obj.nickname,
                               pictures=pictures,
                               user_obj=user_obj,
                               myclubs=myclubs,
                               UserType=UserType)


@userblueprint.route('/submit_info', methods=['POST'])
def personal_submit_info():
    '''Change user's information in database'''
    user_obj = oclubs.objs.User(session['user_id'])
    if request.form['name'] != '':
        user_obj.nickname = request.form['name']
    if request.form['email'] != '':
        user_obj.email = request.form['email']
    if request.form['phone'] != '':
        user_obj.phone = request.form['phone']
    if request.form['picture'] is not None:
        user_obj.picture = oclubs.objs.Upload(request.form['picture'])
    flash('Your information has been successfully changed.', 'status_info')
    return redirect(url_for('.personal'))


@userblueprint.route('/submit_password', methods=['POST'])
def personal_submit_password():
    '''Change user's password in database'''
    user_obj = oclubs.objs.User(session['user_id'])
    user_login = oclubs.objs.User.attempt_login(user_obj.studentid, request.form['old'])
    if user_login is not None:
        if request.form['new'] == request.form['again']:
            user_obj.password = request.form['new']
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
    # accept input  to retrieve password
    pass
