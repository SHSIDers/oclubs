#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from flask import (
    Blueprint, render_template, url_for, request, session, redirect, flash, abort
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
        abort(401)
    user_obj = oclubs.objs.User(session['user_id'])
    try:
        club_id = int(re.match(r'^\d+', club_info).group(0))
        club = oclubs.objs.Club(club_id)
    except:
        abort(404)
    if user_obj.id != club.leader.id:
        abort(403)
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
        abort(404)
    return render_template('clubintro.html',
                           title='Club Intro',
                           user=user,
                           club=club.name,
                           intro=club.intro,
                           leader=club.leader.nickname,
                           picture=club.picture,
                           desc=club.description)


@clubblueprint.route('/<club_info>/club_photo')
def clubphoto(club_info):
    '''Individual Club's Photo Page'''
    if('user_id' in session):
        user_obj = oclubs.objs.User(session['user_id'])
        user = user_obj.nickname
    else:
        user = ''
    try:
        club_id = int(re.match(r'^\d+', club_info).group(0))
        club = oclubs.objs.Club(club_id)
    except:
        abort(404)
    club_name = club.name
    photos = []
    activities_obj = club.activities([True, True, True, False, True])
    photos = [{'image1': 'intro1', 'actname1': 'Random Activity', 'image2': 'intro2', 'actname2': 'Random Activity'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'image2': 'intro2', 'actname2': 'Random Activity'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'image2': 'intro2', 'actname2': 'Random Activity'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'image2': 'intro2', 'actname2': 'Random Activity'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'image2': 'intro2', 'actname2': 'Random Activity'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'image2': 'intro2', 'actname2': 'Random Activity'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'image2': 'intro2', 'actname2': 'Random Activity'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'image2': 'intro2', 'actname2': 'Random Activity'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'image2': 'intro2', 'actname2': 'Random Activity'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'image2': 'intro2', 'actname2': 'Random Activity'}]
    return render_template('clubphoto.html',
                           title=club,
                           user=user,
                           club=club,
                           photos=photos)


@clubblueprint.route('/<club_info>/new_leader')
def newleader(club_info):
    '''Selecting New Club Leader'''
    if 'user_id' not in session:
        abort(401)
    user_obj = oclubs.objs.User(session['user_id'])
    try:
        club_id = int(re.match(r'^\d+', club_info).group(0))
        club = oclubs.objs.Club(club_id)
    except:
        abort(404)
    if user_obj.id != club.leader.id:
        abort(403)
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
                           members=members,
                           club_info=club_info)


@clubblueprint.route('/<club_info>/new_leader/submit', methods=['POST'])
def newleader_submit(club_info):
    '''Change leader in database'''
    user_obj = oclubs.objs.User(session['user_id'])
    club_id = int(re.match(r'^\d+', club_info).group(0))
    club = oclubs.objs.Club(club_id)
    members_obj = club.members
    leader_name = request.form['leader']
    for member_obj in members_obj:
        if leader_name == member_obj.passportname:
            club.leader = member_obj
            break
    return render_template('success.html',
                           title='Success',
                           user=user_obj.nickname)


@clubblueprint.route('/<club_info>/input_attendance')
def inputatten(club_info):
    '''Input Attendance'''
    if 'user_id' not in session:
        abort(401)
    user_obj = oclubs.objs.User(session['user_id'])
    try:
        club_id = int(re.match(r'^\d+', club_info).group(0))
        club = oclubs.objs.Club(club_id)
    except:
        abort(404)
    if user_obj.id != club.leader.id:
        abort(403)
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


@clubblueprint.route('/{club_info>/input_attendance/submit', methods=['POST'])
def inputatten_submit(club_info):
    '''Change attendance in database'''
    pass


@clubblueprint.route('/<club_info>/member_info')
def memberinfo(club_info):
    '''Check Members' Info'''
    if 'user_id' not in session:
        abort(401)
    user_obj = oclubs.objs.User(session['user_id'])
    try:
        club_id = int(re.match(r'^\d+', club_info).group(0))
        club = oclubs.objs.Club(club_id)
    except:
        abort(404)
    if user_obj.id != club.leader.id:
        abort(403)
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


@clubblueprint.route('/<club_info>/change_club_info')
def changeclubinfo(club_info):
    '''Change Club's Info'''
    if 'user_id' not in session:
        abort(401)
    user_obj = oclubs.objs.User(session['user_id'])
    try:
        club_id = int(re.match(r'^\d+', club_info).group(0))
        club = oclubs.objs.Club(club_id)
    except:
        abort(404)
    if user_obj.id != club.leader.id:
        abort(403)
    return render_template('changeclubinfo.html',
                           title='Change Club Info',
                           user=user_obj.nickname,
                           club=club.name,
                           intro=club.intro,
                           picture=club.picture,
                           desc=club.description,
                           club_info=club_info)


@clubblueprint.route('/<club_info>/change_club_info/submit', methods=['POST'])
def changeclubinfo_submit(club_info):
    '''Change club's info'''
    club_id = int(re.match(r'^\d+', club_info).group(0))
    club = oclubs.objs.Club(club_id)
    club.intro = request.form['intro']
    club.picture = request.form['photo']
    club.desc = request.form['desc']
    flash('The information about club has been successfully submitted.', 'success')
    return redirect(url_for('changeclubinfo', club_info=club_info))


@clubblueprint.route('/<club_info>/adjust_member')
def adjustmember(club_info):
    '''Adjust Club Members'''
    if 'user_id' not in session:
        abort(401)
    user_obj = oclubs.objs.User(session['user_id'])
    try:
        club_id = int(re.match(r'^\d+', club_info).group(0))
        club = oclubs.objs.Club(club_id)
    except:
        abort(404)
    if user_obj.id != club.leader.id:
        abort(403)
    members_obj = club.members
    members = []
    for member_obj in members_obj:
        member = {}
        member['nick_name'] = member_obj.nickname
        member['passportname'] = member_obj.passportname
        member['picture'] = member_obj.picture
        member['studentid'] = member_obj.studentid
        member['id'] = member_obj.id
        members.append(member)
    return render_template('adjustmember.html',
                           title='Adjust Members',
                           user=user_obj.nickname,
                           club=club.name,
                           members=members,
                           club_info=club_info)


@clubblueprint.route('/<club_info>/adjust_member/submit', methods=['POST'])
def adjustmember_submit(club_info):
    '''Input adjustment of club members'''
    club_id = int(re.match(r'^\d+', club_info).group(0))
    club = oclubs.objs.Club(club_id)
    member_obj = oclubs.objs.User(request.form['expel'])
    club.remove_member(member_obj)
    flash(member_obj.nickname + ' has been expelled.', 'expelled')
    return redirect(url_for('adjustmember', club_info=club_info))
