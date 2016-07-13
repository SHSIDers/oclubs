#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from flask import (
    Blueprint, render_template, url_for, request, session, redirect
)

import traceback
import oclubs
import re

clubblueprint = Blueprint('clubblueprint', __name__)


@clubblueprint.route('/clublist')
def clublist():
    '''Club List'''
    if('user_id' in session):
        user = oclubs.objs.User(session['user_id']).nickname
    else:
        user = ''
    # randomly choose clubs
    clubs = [{'name': 'Art Club', 'photo': 'intro1', 'intro': 'Here is where birth of arts happens'},
             {'name': 'Photo Club', 'photo': 'intro2', 'intro': 'Place for photography!'},
             {'name': 'Art Club', 'photo': 'intro3', 'intro': 'Here is where birth of arts happens'},
             {'name': 'Photo Club', 'photo': 'intro3', 'intro': 'Place for photography!'},
             {'name': 'Art Club', 'photo': 'intro4', 'intro': 'Here is where birth of arts happens'},
             {'name': 'Photo Club', 'photo': 'intro5', 'intro': 'Place for photography!'},
             {'name': 'Art Club', 'photo': 'intro6', 'intro': 'Here is where birth of arts happens'},
             {'name': 'Photo Club', 'photo': 'intro7', 'intro': 'Place for photography!'},
             {'name': 'Art Club', 'photo': 'intro8', 'intro': 'Here is where birth of arts happens'},
             {'name': 'Photo Club', 'photo': 'intro9', 'intro': 'Place for photography!'}]
    return render_template('clublist.html',
                           title='Club List',
                           is_list=True,
                           user=user,
                           clubs=clubs)


@clubblueprint.route('/<club_info>')
def club(club_info):
    '''Club Management Page'''
    if 'user_id' not in session:
        return redirect(url_for('notloggedin'))
    user_obj = oclubs.objs.User(session['user_id'])
    try:
        club_id = int(re.match(r'^\d+', club_info).group(0))
        club = oclubs.objs.Club(club_id)
    except:
        return redirect(url_for('wrongurl'))
    if user_obj.id != club.leader.id:
        return redirect(url_for('noaccess'))
    return render_template('club.html',
                           title=club.name,
                           user=user_obj.nickname,
                           club=club.name)


@clubblueprint.route('/<club_info>/introduction')
def clubintro(club_info):
    '''Club Intro'''
    if('user_id' in session):
        user = oclubs.objs.User(session['user_id']).nickname
    else:
        user = ''
    try:
        club_id = int(re.match(r'^\d+', club_info).group(0))
        club = oclubs.objs.Club(club_id)
    except:
        return redirect(url_for('wrongurl'))
    return render_template('clubintro.html',
                           title='Club Intro',
                           user=user,
                           club=club.name,
                           intro=club.intro,
                           leader=club.leader.nickname,
                           picture=club.picture,
                           desc=club.description)


@clubblueprint.route('/<club_info>/new_leader', methods=['GET', 'POST'])
def newleader(club_info):
    '''Selecting New Club Leader'''
    if request.method == 'GET':
        if 'user_id' not in session:
            return redirect(url_for('notloggedin'))
        user_obj = oclubs.objs.User(session['user_id'])
        try:
            club_id = int(re.match(r'^\d+', club_info).group(0))
            club = oclubs.objs.Club(club_id)
        except:
            return redirect(url_for('wrongurl'))
        if user_obj.id != club.leader.id:
            return redirect(url_for('noaccess'))
        leader = {}
        leader['passportname'] = user_obj.passportname
        leader['nick_name'] = user_obj.nickname
        leader['picture'] = user_obj.picture
        members_obj = club.members
        members = []
        for member_obj in members_obj:
            member = {}
            member['passportname'] = member_obj.passportname
            member['nick_name'] = member_obj.nickname
            member['picture'] = member_obj.picture
            members.append(member)
        return render_template('newleader.html',
                               title='New Leader',
                               user=user_obj.nickname,
                               club=club.name,
                               leader=leader,
                               members=members)
    if request.method == 'POST':
        # change club leader
        pass


@clubblueprint.route('/<club_info>/input_attendance', methods=['GET', 'POST'])
def inputatten(club_info):
    '''Input Attendance'''
    if request.method == 'GET':
        if 'user_id' not in session:
            return redirect(url_for('notloggedin'))
        user_obj = oclubs.objs.User(session['user_id'])
        try:
            club_id = int(re.match(r'^\d+', club_info).group(0))
            club = oclubs.objs.Club(club_id)
        except:
            return redirect(url_for('wrongurl'))
        if user_obj.id != club.leader.id:
            return redirect(url_for('noaccess'))
        members_obj = club.members
        members = []
        for member_obj in members_obj:
            member = {}
            member['passportname'] = member_obj.passportname
            member['nick_name'] = member_obj.nickname
            member['picture'] = member_obj.picture
            members.append(member)
        return render_template('inputatten.html',
                               title='Input Attendance',
                               user=user_obj.nickname,
                               club=club.name,
                               members=members)
    if request.method == 'POST':
        # input attendance
        pass


@clubblueprint.route('/<club_info>/member_info')
def memberinfo(club_info):
    '''Check Members' Info'''
    if 'user_id' not in session:
        return redirect(url_for('notloggedin'))
    user_obj = oclubs.objs.User(session['user_id'])
    try:
        club_id = int(re.match(r'^\d+', club_info).group(0))
        club = oclubs.objs.Club(club_id)
    except:
        return redirect(url_for('wrongurl'))
    if user_obj.id != club.leader.id:
        return redirect(url_for('noaccess'))
    members_obj = club.members
    members = []
    for member_obj in members_obj:
        member = {}
        member['nick_name'] = member_obj.nickname
        member['id'] = member_obj.studentid
        member['passportname'] = member_obj.passportname
        member['email'] = member_obj.email
        members.append(member)
    return render_template('memberinfo.html',
                           title='Member Info',
                           user=user_obj.nickname,
                           club=club.name,
                           members=members)


@clubblueprint.route('/<club_info>/change_club_info', methods=['GET', 'POST'])
def changeclubinfo(club_info):
    '''Change Club's Info'''
    if request.method == 'GET':
        if 'user_id' not in session:
            return redirect(url_for('notloggedin'))
        user_obj = oclubs.objs.User(session['user_id'])
        try:
            club_id = int(re.match(r'^\d+', club_info).group(0))
            club = oclubs.objs.Club(club_id)
        except:
            return redirect(url_for('wrongurl'))
        if user_obj.id != club.leader.id:
            return redirect(url_for('noaccess'))
        return render_template('changeclubinfo.html',
                               title='Change Club Info',
                               user=user_obj.nickname,
                               club=club.name,
                               intro=club.intro,
                               picture=club.picture,
                               desc=club.description)
    if request.method == 'POST':
        club_id = int(re.match(r'^\d+', club_info).group(0))
        club = oclubs.objs.Club(club_id)
        club.intro = request.form['intro']
        club.picture = request.form['photo']
        club.desc = request.form['desc']
        return render_template('')


@clubblueprint.route('/<club_info>/adjust_member', methods=['GET', 'POST'])
def adjustmember(club_info):
    '''Adjust Club Members'''
    if request.method == 'GET':
        if 'user_id' not in session:
            return redirect(url_for('notloggedin'))
        user_obj = oclubs.objs.User(session['user_id'])
        try:
            club_id = int(re.match(r'^\d+', club_info).group(0))
            club = oclubs.objs.Club(club_id)
        except:
            return redirect(url_for('wrongurl'))
        if user_obj.id != club.leader.id:
            return redirect(url_for('noaccess'))
        members_obj = club.members
        members = []
        for member_obj in members_obj:
            member = {}
            member['nick_name'] = member_obj.nickname
            member['passportname'] = member_obj.passportname
            member['picture'] = member_obj.picture
            member['id'] = member_obj.studentid
            members.append(member)
        return render_template('adjustmember.html',
                               title='Adjust Members',
                               user=user_obj.nickname,
                               club=club.name,
                               members=members)
    if request.method == 'POST':
        # expel member
        pass


@clubblueprint.route('/no_access')
def noaccess():
    user_obj = oclubs.objs.User(session['user_id'])
    return render_template('noaccess.html',
                           title='No Access',
                           user=user_obj.nickname)


@clubblueprint.route('/wrong_url')
def wrongurl():
    if 'user_id' in session:
        user = oclubs.objs.User(session['user_id']).nickname
    else:
        user = ''
    return render_template('wrongurl.html',
                           title='Wrong URL',
                           user=user)


@clubblueprint.route('/not_logged_in')
def notloggedin():
    return render_template('notloggedin.html',
                           title='Not Logged In',
                           user='')
