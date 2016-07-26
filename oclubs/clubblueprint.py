#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

import re

from flask import (
    Blueprint, render_template, url_for, request, session, redirect, flash, abort
)
from flask_login import current_user, login_required

from oclubs.objs import User, Club, Upload
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
    return render_template('club/clublist.html',
                           title='Club List',
                           is_list=True,
                           clubs=clubs,
                           club_type=club_type)


@clubblueprint.route('/<club>/manage')
@get_callsign(Club, 'club')
@special_access_required
def club(club):
    '''Club Management Page'''
    return render_template('club/clubmanage.html',
                           title=club.name,
                           club=club.name)


@clubblueprint.route('/<club>/introduction')
@get_callsign(Club, 'club')
def clubintro(club):
    '''Club Intro'''
    return render_template('club/clubintro.html',
                           title='Club Intro')


@clubblueprint.route('/<club>/introduction/submit')
@get_callsign(Club, 'club')
@login_required
def clubintro_submit(club):
    '''Add new member'''
    club.add_member(current_user)
    flash('You have successfully joined ' + club.name + '.', 'join')
    return redirect(url_for('.clubintro', club=club.callsign))


@clubblueprint.route('/<club>/new_leader')
@get_callsign(Club, 'club')
@login_required  # FIXME: fresh_login_required
@special_access_required
def newleader(club):
    '''Selecting New Club Leader'''
    return render_template('club/newleader.html',
                           title='New Leader')


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
    return render_template('club/success.html',
                           title='Success')


@clubblueprint.route('/<club>/member_info')
@get_callsign(Club, 'club')
@special_access_required
def memberinfo(club):
    '''Check Members' Info'''
    return render_template('club/memberinfo.html',
                           title='Member Info',
                           club=club)


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
    return download_csv('Member Info.csv', header, info)


@clubblueprint.route('/<club>/change_club_info')
@get_callsign(Club, 'club')
@special_access_required
def changeclubinfo(club):
    '''Change Club's Info'''
    return render_template('club/changeclubinfo.html',
                           title='Change Club Info')


@clubblueprint.route('/<club>/change_club_info/submit', methods=['POST'])
@get_callsign(Club, 'club')
@special_access_required
def changeclubinfo_submit(club):
    '''Change club's info'''
    if request.form['intro'] != '':
        club.intro = request.form['intro']
    if request.form['description'] != '':
        club.desc = request.form['description']
    # upload_picture(club)
    flash('The information about club has been successfully submitted.', 'success')
    return redirect(url_for('.changeclubinfo', club=club.callsign))


@clubblueprint.route('/<club>/adjust_member')
@get_callsign(Club, 'club')
@special_access_required
def adjustmember(club):
    '''Adjust Club Members'''
    return render_template('club/adjustmember.html',
                           title='Adjust Members')


@clubblueprint.route('/<club>/adjust_member/submit/<studentid>', methods=['POST'])
@get_callsign(Club, 'club')
@special_access_required
def adjustmember_submit(club, studentid):
    '''Input adjustment of club members'''
    member_obj = User(studentid)
    club.remove_member(member_obj)
    flash(member_obj.nickname + ' has been expelled.', 'expelled')
    return redirect(url_for('.adjustmember', club=club.callsign))
