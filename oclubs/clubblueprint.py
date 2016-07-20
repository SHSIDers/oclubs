#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

from flask import (
    Blueprint, render_template, url_for, request, session, redirect, flash, abort
)

import oclubs
import re
from oclubs.enums import UserType, ClubType, ActivityTime

clubblueprint = Blueprint('clubblueprint', __name__)


def get_club(club_info):
    '''From club_info get club object'''
    try:
        club_id = int(re.match(r'^\d+', club_info).group(0))
        club = oclubs.objs.Club(club_id)
    except (NameError, AttributeError, OverflowError):
        abort(404)
    return club


@clubblueprint.route('/clublist/<type>')
def clublist(type):
    '''Club list by club type'''
    num = 18
    if type == 'all':
        clubs_obj = oclubs.objs.Club.randomclubs(num)
    elif type != '':
        clubs_obj = oclubs.objs.Club.randomclubs(num, [ClubType[type.upper()]])
    else:
        abort(404)
    clubs = []
    for club_obj in clubs_obj:
        club = {}
        club['id'] = club_obj.id
        club['name'] = club_obj.name
        club['picture'] = club_obj.picture
        club['intro'] = club_obj.intro
        clubs.append(club)
    return render_template('clublist.html',
                           title='Club List',
                           is_list=True,
                           clubs=clubs,
                           type=type)


@clubblueprint.route('/<club_info>')
def club(club_info):
    '''Club Management Page'''
    if 'user_id' not in session:
        abort(401)
    user_obj = oclubs.objs.User(session['user_id'])
    club = get_club(club_info)
    if user_obj.id != club.leader.id:
        abort(403)
    return render_template('club.html',
                           title=club.name,
                           club=club.name,
                           club_info=club_info)


@clubblueprint.route('/<club_info>/introduction')
def clubintro(club_info):
    '''Club Intro'''
    club = get_club(club_info)
    return render_template('clubintro.html',
                           title='Club Intro',
                           club=club.name,
                           intro=club.intro,
                           leader=club.leader.nickname,
                           picture=club.picture,
                           desc=club.description,
                           club_info=club_info)


@clubblueprint.route('/<club_info>/introduction/submit')
def clubintro_submit(club_info):
    '''Add new member'''
    if 'user_id' not in session:
        abort(401)
    user_obj = oclubs.objs.User(session['user_id'])
    club = get_club(club_info)
    club.add_member(user_obj)
    flash('You have successfully joined ' + club.name + '.', 'join')
    return redirect(url_for('clubblueprint.clubintro', club_info=club_info))


@clubblueprint.route('/<club_info>/new_leader')
def newleader(club_info):
    '''Selecting New Club Leader'''
    if 'user_id' not in session:
        abort(401)
    user_obj = oclubs.objs.User(session['user_id'])
    club = get_club(club_info)
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
                           club=club.name,
                           leader=leader,
                           members=members,
                           club_info=club_info)


@clubblueprint.route('/<club_info>/new_leader/submit', methods=['POST'])
def newleader_submit(club_info):
    '''Change leader in database'''
    club = get_club(club_info)
    members_obj = club.members
    leader_name = request.form['leader']
    for member_obj in members_obj:
        if leader_name == member_obj.passportname:
            club.leader = member_obj
            break
    return render_template('success.html',
                           title='Success')


@clubblueprint.route('/<club_info>/member_info')
def memberinfo(club_info):
    '''Check Members' Info'''
    if 'user_id' not in session:
        abort(401)
    user_obj = oclubs.objs.User(session['user_id'])
    club = get_club(club_info)
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
                           club=club.name,
                           members=members)


@clubblueprint.route('/<club_info>/change_club_info')
def changeclubinfo(club_info):
    '''Change Club's Info'''
    if 'user_id' not in session:
        abort(401)
    user_obj = oclubs.objs.User(session['user_id'])
    club = get_club(club_info)
    if user_obj.id != club.leader.id:
        abort(403)
    return render_template('changeclubinfo.html',
                           title='Change Club Info',
                           club=club.name,
                           intro=club.intro,
                           picture=club.picture,
                           desc=club.description,
                           club_info=club_info)


@clubblueprint.route('/<club_info>/change_club_info/submit', methods=['POST'])
def changeclubinfo_submit(club_info):
    '''Change club's info'''
    club = get_club(club_info)
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
    club = get_club(club_info)
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
                           club=club.name,
                           members=members,
                           club_info=club_info)


@clubblueprint.route('/<club_info>/adjust_member/submit', methods=['POST'])
def adjustmember_submit(club_info):
    '''Input adjustment of club members'''
    club = get_club(club_info)
    member_obj = oclubs.objs.User(request.form['expel'])
    club.remove_member(member_obj)
    flash(member_obj.nickname + ' has been expelled.', 'expelled')
    return redirect(url_for('adjustmember', club_info=club_info))
