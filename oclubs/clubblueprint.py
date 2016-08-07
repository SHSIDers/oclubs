#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

import re

from flask import (
    Blueprint, render_template, url_for, request, session, redirect, flash, abort
)
from flask_login import current_user, login_required

from oclubs.objs import User, Club, Upload, FormattedText
from oclubs.enums import UserType, ClubType, ActivityTime, ClubJoinMode
from oclubs.shared import (
    download_xlsx, get_callsign, special_access_required, render_email_template
)
from oclubs.access import email

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
                           title=club.name)


@clubblueprint.route('/<club>/introduction')
@get_callsign(Club, 'club')
def clubintro(club):
    '''Club Intro'''
    if current_user.is_active:
        free_join = (club.joinmode == ClubJoinMode.FREE_JOIN) and \
                    (current_user.type == UserType.STUDENT) and \
                    (current_user not in club.members)
    else:
        free_join = False
    return render_template('club/clubintro.html',
                           title='Club Intro',
                           free_join=free_join)


@clubblueprint.route('/<club>/introduction/submit')
@get_callsign(Club, 'club')
@login_required
def clubintro_submit(club):
    '''Add new member'''
    club.add_member(current_user)
    parameters = {'club': club, 'current_user': current_user}
    contents = render_email_template('joinclubs', parameters)
    # club.leader.email_user('New Club Member - ' + club.name, contents)
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
    leader_old = club.leader
    members_obj = club.members
    leader_name = request.form['leader']
    for member_obj in members_obj:
        if leader_name == member_obj.passportname:
            club.leader = member_obj
            break
    for member in club.members:
        parameters = {'user': member, 'club': club, 'leader_old': leader_old}
        contents = render_email_template('newleader', parameters)
        # member.email_user('New Leader - ' + club.name, contents)
    return render_template('club/success.html',
                           title='Success')


@clubblueprint.route('/<club>/member_info')
@get_callsign(Club, 'club')
def memberinfo(club):
    '''Check Members' Info'''
    has_access = (current_user.id == club.leader.id or
                  current_user.id == club.teacher.id or
                  current_user.type == UserType.ADMIN)
    return render_template('club/memberinfo.html',
                           title='Member Info',
                           has_access=has_access)


@clubblueprint.route('/<club>/member_info/download')
@get_callsign(Club, 'club')
@special_access_required
def memberinfo_download(club):
    '''Download members' info'''
    info = []
    info.append(['Nick Name', 'Student ID', 'Passport Name', 'Email'])
    members = club.members
    for member in members:
        info_each = []
        info_each.append(member.nickname)
        info_each.append(member.studentid)
        info_each.append(member.passportname)
        info_each.append(member.email)
        info.append(info_each)
    return download_xlsx('Member Info.xlsx', info)


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
        club.description = FormattedText.handle(current_user, club, request.form['description'])
    if request.files['picture'].filename != '':
        club.picture = Upload.handle(current_user, club, request.files['picture'])
    for member in club.members:
        parameters = {'user': member, 'club': club}
        contents = render_email_template('changeclubinfo', parameters)
        # member.email_user('Change Club Info - ' + club.name, contents)
    flash('The information about club has been successfully submitted.', 'success')
    return redirect(url_for('.changeclubinfo', club=club.callsign))


@clubblueprint.route('/<club>/adjust_member')
@get_callsign(Club, 'club')
@special_access_required
def adjustmember(club):
    '''Adjust Club Members'''
    return render_template('club/adjustmember.html',
                           title='Adjust Members')


@clubblueprint.route('/<club>/adjust_member/submit', methods=['POST'])
@get_callsign(Club, 'club')
@special_access_required
def adjustmember_submit(club):
    '''Input adjustment of club members'''
    member = User(request.form['studentid'])
    club.remove_member(member)
    parameters = {'member': member, 'club': club}
    contents = render_email_template('adjustmember', parameters)
    # member.email_user('Member Adjustment - ' + club.name, contents)
    flash(member.nickname + ' has been expelled.', 'expelled')
    return redirect(url_for('.adjustmember', club=club.callsign))
