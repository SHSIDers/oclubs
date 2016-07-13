#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from flask import (
    Blueprint, render_template, url_for, request, session, redirect
)

import traceback
import oclubs

userblueprint = Blueprint('userblueprint', __name__)


@userblueprint.route('/quit_club', methods=['GET', 'POST'])
def quitclub():
    '''Quit Club Page'''
    if request.method == 'GET':
        if 'user_id' not in session:
            return redirect(url_for('notloggedin'))
        user_obj = oclubs.objs.User(session['user_id'])
        clubs_obj = user_obj.clubs
        clubs = []
        for club_obj in clubs_obj:
            clubs.append(club_obj.name)
        return render_template('quitclub.html',
                               title='Quit Club',
                               user=user_obj.nickname,
                               clubs=clubs)
    if request.method == 'POST':
        # delete connection between user and club
        pass


@userblueprint.route('/register_hongmei')
def registerhm():
    '''Register Page for HongMei Activites'''
    user = ''
    club = 'Website Club'
    schedule = [{'id': '1', 'date': 'June 6 2016', 'activity': 'Finish homepage design'},
                {'id': '2', 'date': 'June 7 2016', 'activity': 'Finish activity page design'},
                {'id': '3', 'date': 'June 8 2016', 'activity': 'Finish personal page design'},
                {'id': '4', 'date': 'June 9 2016', 'activity': 'Finish club page design'},
                {'id': '5', 'date': 'June 10 2016', 'activity': 'Finish photo page design'},
                {'id': '6', 'date': 'June 11 2016', 'activity': 'Finish about page design'},
                {'id': '7', 'date': 'June 6 2016', 'activity': 'Finish homepage design'},
                {'id': '8', 'date': 'June 7 2016', 'activity': 'Finish activity page design'},
                {'id': '9', 'date': 'June 8 2016', 'activity': 'Finish personal page design'},
                {'id': '10', 'date': 'June 9 2016', 'activity': 'Finish club page design'},
                {'id': '11', 'date': 'June 10 2016', 'activity': 'Finish photo page design'},
                {'id': '12', 'date': 'June 11 2016', 'activity': 'Finish about page design'},
                {'id': '13', 'date': 'June 6 2016', 'activity': 'Finish homepage design'},
                {'id': '14', 'date': 'June 7 2016', 'activity': 'Finish activity page design'},
                {'id': '15', 'date': 'June 8 2016', 'activity': 'Finish personal page design'},
                {'id': '16', 'date': 'June 9 2016', 'activity': 'Finish club page design'},
                {'id': '17', 'date': 'June 10 2016', 'activity': 'Finish photo page design'},
                {'id': '18', 'date': 'June 11 2016', 'activity': 'Finish about page design'}]
    return render_template('registerhm.html',
                           title='Register for HongMei',
                           user=user,
                           club=club,
                           schedule=schedule)


@userblueprint.route('/', methods=['GET', 'POST'])
def personal():
    '''Student Personal Page'''
    if request.method == 'GET':
        if 'user_id' not in session:
            return redirect(url_for('notloggedin'))
        user_obj = oclubs.objs.User(session['user_id'])
        if user_obj.type == 1:
            return redirect(url_for('noaccess'))
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
            # club['cas'] = user_obj.
        evaluate = False
        castotal = 0
        for club in clubs:
            castotal += club['cas']
        activities = [{'club': 'Website Club', 'act': 'Create Club Platform', 'time': 'Forever', 'place': 'Home'},
                      {'club': 'Chess Club', 'act': 'Chess Tournament', 'time': 'June 1, 2011', 'place': 'XMT 201'},
                      {'club': 'Math Club', 'act': 'Do Math Homework', 'time': 'July 2, 2012', 'place': 'Home'}]
        hongmei = [{'club': 'Chess Club', 'act': 'Teach Basic Rules of Chess', 'time': 'March 2, 2012'},
                   {'club': 'Math Club', 'act': 'Teach Multiplication', 'time': 'March 9, 2012'}]
        for club_obj in clubs_obj:
            if user_obj.id == club_obj.leader.id:
                leader_club = club_obj.name
                break
        return render_template('personal.html',
                               title=user_obj.nickname,
                               user=user_obj.nickname,
                               pictures=pictures,
                               info=info,
                               clubs=clubs,
                               evaluate=evaluate,
                               castotal=castotal,
                               activities=activities,
                               hongmei=hongmei,
                               leader_club=leader_club)
    if request.method == 'POST':
        user_obj = oclubs.objs.User(session['user_id'])
        if request.form['change_info'] == 'Change Info':
            user_obj.nickname = request.form['name']
            user_obj.email = request.form['email']
            user_obj.phone = request.form['phone']
            user_obj.picture = request.form['picture']  # location in html has to be adjusted
        if request.form['change_pass'] == 'Change Password':
            if request.form['new'] == request.form['again']:
                user_obj.password = request.form['new']


@userblueprint.route('/teacher', methods=['GET', 'POST'])
def teacher():
    '''Teacher Page'''
    if request.method == 'GET':
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
                               user=user_obj.nickname,
                               myclubs=myclubs,
                               pictures=pictures,
                               info=info)
    if request.method == 'POST':
        # change info
        user_obj = oclubs.objs.User(session['user_id'])
        if request.form['change_info'] == 'Change Info':
            user_obj.nickname = request.form['name']
            user_obj.email = request.form['email']
            user_obj.phone = request.form['phone']
            user_obj.picture = request.form['picture']  # location in html has to be adjusted
        if request.form['change_pass'] == 'Change Password':
            if request.form['new'] == request.form['again']:
                user_obj.password = request.form['new']


@userblueprint.route('/forgot_password', methods=['GET', 'POST'])
def forgotpw():
    '''Page for retrieving password'''
    if request.method == 'GET':
        if('user_id' in session):
            user = oclubs.objs.User(session['user_id']).nickname
        else:
            user = ''
        return render_template('forgotpassword.html',
                               title='Retrieve Password',
                               user=user)
    if request.method == 'POST':
        # accept input to retrieve password
        pass
