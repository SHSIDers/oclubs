#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

import re

from flask import (
    Blueprint, render_template, url_for, request, session, redirect, flash, abort
)
from flask_login import current_user, login_required

from oclubs.objs import User, Club
from oclubs.enums import UserType, ClubType, ActivityTime
from oclubs.shared import download_csv, upload_picture, get_callsign, special_access_required

clubblueprint = Blueprint('clubblueprint', __name__)


@clubblueprint.route('/clublist/<club_type>')
def clublist(club_type):
    '''Club list by club type'''
    num = 18
    if club_type == 'all':
        clubs = Club.randomclubs(num)
    elif club_type == 'excellent':
        clubs = Club.excellentclubs()
    else:
        try:
            clubs = Club.randomclubs(num, [ClubType[club_type.upper()]])
        except KeyError:
            abort(404)
    return render_template('clublist.html',
                           title='Club List',
                           is_list=True,
                           clubs=clubs,
                           club_type=club_type)


@clubblueprint.route('/<club>/management')
@get_callsign(Club, 'club')
@special_access_required
def club(club):
    '''Club Management Page'''
    return render_template('club.html',
                           title=club.name,
                           club=club.name)


@clubblueprint.route('/<club>/introduction')
@get_callsign(Club, 'club')
def clubintro(club):
    '''Club Intro'''
    return render_template('clubintro.html',
                           title='Club Intro')


@clubblueprint.route('/<club>/introduction/submit')
@get_callsign(Club, 'club')
@login_required
def clubintro_submit(club):
    '''Add new member'''
    club.add_member(current_user)
    flash('You have successfully joined ' + club.name + '.', 'join')
    return redirect(url_for('clubblueprint.clubintro', club=club.callsign))


@clubblueprint.route('/<club>/new_leader')
@get_callsign(Club, 'club')
@login_required  # FIXME: fresh_login_required
@special_access_required
def newleader(club):
    '''Selecting New Club Leader'''
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
                           leader=current_user,
                           members=members)


@clubblueprint.route('/<club>/new_leader/submit', methods=['POST'])
@get_callsign(Club, 'club')
@login_required  # FIXME: fresh_login_required
@special_access_required
def newleader_submit(club):
    '''Change leader in database'''
    members_obj = club.members
    leader_name = request.form['leader']
    for member_obj in members_obj:
        if leader_name == member_obj.passportname:
            club.leader = member_obj
            break
    return render_template('success.html',
                           title='Success')


@clubblueprint.route('/<club>/member_info')
@get_callsign(Club, 'club')
@special_access_required
def memberinfo(club):
    '''Check Members' Info'''
    return render_template('memberinfo.html',
                           title='Member Info',
                           club=club.name,
                           members=club.members)


@clubblueprint.route('/<club>/member_info/download')
@get_callsign(Club, 'club')
@special_access_required
def memberinfo_download(club):
    '''Download members' info'''
    header = ['Nick Name', 'Student ID', 'Passport Name', 'Email']
    info = []
    members = club.members
    for member in members:
        info_each = []
        info_each.append(member.nickname)
        info_each.append(member.studentid)
        info_each.append(member.passportname)
        info_each.append(member.email)
        info.append(info_each)
    info.append(['哈哈哈', '哈哈哈', '哈哈哈', '哈哈哈'])
    return download_csv('Member Info.csv', header, info)


@clubblueprint.route('/<club>/change_club_info')
@get_callsign(Club, 'club')
@special_access_required
def changeclubinfo(club):
    '''Change Club's Info'''
    return render_template('changeclubinfo.html',
                           title='Change Club Info',
                           club=club.name,
                           intro=club.intro,
                           picture=club.picture,
                           desc=club.description.formatted)


@clubblueprint.route('/<club>/change_club_info/submit', methods=['POST'])
@get_callsign(Club, 'club')
@special_access_required
def changeclubinfo_submit(club):
    '''Change club's info'''
    upload_picture(club)
    club.intro = request.form['intro']
    club.desc = request.form['desc']
    flash('The information about club has been successfully submitted.', 'success')
    return redirect(url_for('.changeclubinfo', club=club.callsign))


@clubblueprint.route('/<club>/adjust_member')
@get_callsign(Club, 'club')
@special_access_required
def adjustmember(club):
    '''Adjust Club Members'''
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
                           members=members)


@clubblueprint.route('/<club>/adjust_member/submit', methods=['POST'])
@get_callsign(Club, 'club')
@special_access_required
def adjustmember_submit(club):
    '''Input adjustment of club members'''
    member_obj = User(request.form['expel'])
    club.remove_member(member_obj)
    flash(member_obj.nickname + ' has been expelled.', 'expelled')
    return redirect(url_for('.adjustmember', club=club.callsign))
