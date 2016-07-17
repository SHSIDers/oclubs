#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from flask import (
    Blueprint, render_template, url_for, request, session, redirect, abort, flash
)

import oclubs

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
    flash('You have successfully quitted' + request.form['clubs'], 'quit')
    return redirect(url_for('quitclub'))


@userblueprint.route('/')
def personal():
    '''Student Personal Page'''
    if 'user_id' not in session:
        abort(401)
    user_obj = oclubs.objs.User(session['user_id'])
    if user_obj.type == 1:
        abort(403)
    pictures = []
    for num in range(1, 21):
        pictures.append(num)
    info = {}
    info['name'] = user_obj.nickname
    info['email'] = user_obj.email
    info['picture'] = user_obj.picture
    info['ID'] = user_obj.studentid
    info['phone'] = user_obj.phone
    clubs_obj = user_obj.clubs
    clubs = []
    for club_obj in clubs_obj:
        club = {}
        club['name'] = club_obj.name
        club['picture'] = club.picture
        club['intro'] = club.intro
        club['cas'] = user_obj.cas_in_club(club_obj)
    castotal = 0
    for club in clubs:
        castotal += club['cas']
    meetings_obj = user_obj.activities_reminder([False, True, True, False, False])
    meetings = []
    for meeting_obj in meetings_obj:
        meeting = {}
        meeting['club'] = meeting_obj.club
        date = str(meeting_obj.date)
        time_int = meeting_obj.time
        if time_int == 1:
            time = "Noon"
        else:
            time = "Afternoon"
        meeting['time'] = date[0:4] + " - " + date[4:6] + " - " + date[6:8] + ": " + time
        meeting['location'] = meeting_obj.location
        meetings.append(meeting)
    activities_obj = user_obj.activities_reminder([True, False, False, True, True])
    activities = []
    for act_obj in activities_obj:
        act = {}
        act['club'] = act_obj.club
        date = str(act_obj.date)
        time_int = act_obj.time
        if time_int == 0:
            time = "Unknown time"
        elif time_int == 3:
            time = "HongMei activity"
        else:
            time = "Individual club activity"
        act['time'] = date[0:4] + " - " + date[4:6] + " - " + date[6:8] + ": " + time
        act['location'] = act_obj.location
        activities.append(act)
    leader_club = ''
    for club_obj in clubs_obj:
        if user_obj.id == club_obj.leader.id:
            leader_club = club_obj.name
            break
    return render_template('personal.html',
                           title=user_obj.nickname,
                           pictures=pictures,
                           info=info,
                           clubs=clubs,
                           castotal=castotal,
                           meetings=meetings,
                           activities=activities,
                           leader_club=leader_club)


@userblueprint.route('/submit_info', methods=['POST'])
def personal_submit_info():
    '''Change user's information in database'''
    user_obj = oclubs.objs.User(session['user_id'])
    user_obj.nickname = request.form['name']
    user_obj.email = request.form['email']
    user_obj.phone = request.form['phone']
    user_obj.picture = request.form['picture']  # location in html has to be adjusted
    flash('Your information has been successfully changed.', 'status_info')
    return redirect(url_for('personal'))


@userblueprint.route('/submit_password', methods=['POST'])
def personal_submit_password():
    '''Change user's password in database'''
    if request.form['new'] == request.form['again']:
        user_obj = oclubs.objs.User(session['user_id'])
        user_obj.password = request.form['new']
        flash('Your information has been successfully changed.', 'status_pw')
    else:
        flash('You have entered two different passwords. Please enter again.', 'status_pw')
    return redirect(url_for('personal'))


@userblueprint.route('/teacher')
def teacher():
    '''Teacher Page'''
    if 'user_id' not in session:
        return redirect(url_for('notloggedin'))
    user_obj = oclubs.objs.User(session['user_id'])
    if user_obj.type == 0:
        return redirect(url_for('noaccess'))
    myclubs = user_obj.clubs
    pictures = []
    for num in range(1, 21):
        pictures.append(num)
    info = {}
    info['name'] = user_obj.nickname
    info['email'] = user_obj.email
    info['picture'] = user_obj.picture
    return render_template('teacher.html',
                           title=user_obj.nickname,
                           myclubs=myclubs,
                           pictures=pictures,
                           info=info)


@userblueprint.route('/teacher/submit_info', methods=['POST'])
def teacher_submit_info():
    '''Change teacher's information in database'''
    user_obj = oclubs.objs.User(session['user_id'])
    user_obj.nickname = request.form['name']
    user_obj.email = request.form['email']
    user_obj.phone = request.form['phone']
    user_obj.picture = request.form['picture']  # location in html has to be adjusted
    flash('Your information has been successfully changed.', 'status_info')
    return redirect(url_for('teacher'))


@userblueprint.route('/teacher/submit_password', methods=['POST'])
def teacher_submit_password():
    '''Change teacher's password in database'''
    if request.form['new'] == request.form['again']:
        user_obj = oclubs.objs.User(session['user_id'])
        user_obj.password = request.form['new']
        flash('Your information has been successfully changed.', 'status_pw')
    else:
        flash('You have entered two different passwords. Please enter again.', 'status_pw')
    return redirect(url_for('teacher'))


@userblueprint.route('/forgot_password')
def forgotpw():
    '''Page for retrieving password'''
    return render_template('forgotpassword.html',
                           title='Retrieve Password')


@userblueprint.route('/forgot_password/submit', methods=['POST'])
def forgotpw_submit():
    # accept input  to retrieve password
    pass
