#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from flask import (
    Blueprint, render_template, url_for, request, session
)

import traceback
import oclubs

clubblueprint = Blueprint('clubblueprint', __name__)


@clubblueprint.route('/<club_id>')
@clubblueprint.route('/<club_id><club_name>')
def club(club_id, club_name=''):
    '''Club Management Page'''
    if('user_id' in session):
        user = oclubs.objs.User(session['user_id']).nickname
    else:
        user = ''
    club = oclubs.objs.Club(club_id).name
    return render_template('club.html',
                           title=club,
                           user=user,
                           club=club)


@clubblueprint.route('/clublist')
def clublist():
    '''Club List'''
    user = ''
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


@clubblueprint.route('/clubintro')
def clubintro():
    '''Club Intro'''
    user = ''
    club = 'Website Club'
    one = 'We create oClubs for SHSID clubs.'
    leader = 'Derril'
    quote = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
    person = 'Lorem'
    photo = 'intro5'
    intro = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
    return render_template('clubintro.html',
                           title='Club Intro',
                           user=user,
                           club=club,
                           one=one,
                           leader=leader,
                           quote=quote,
                           person=person,
                           photo=photo,
                           intro=intro)


@clubblueprint.route('/newleader')
def newleader():
    '''Selecting New Club Leader'''
    user = ''
    leader = {'official_name': 'Feng Ma', 'nick_name': 'Principal Ma', 'photo': '4'}
    members = [{'official_name': 'Ichiro Tai', 'nick_name': 'Derril', 'photo': '1'},
               {'official_name': 'YiFei Zhu', 'nick_name': 'YiFei', 'photo': '2'},
               {'official_name': 'Frank Lee', 'nick_name': 'Frank', 'photo': '3'},
               {'official_name': 'Ichiro Tai', 'nick_name': 'Derril', 'photo': '1'},
               {'official_name': 'YiFei Zhu', 'nick_name': 'YiFei', 'photo': '2'},
               {'official_name': 'Frank Lee', 'nick_name': 'Frank', 'photo': '3'},
               {'official_name': 'Ichiro Tai', 'nick_name': 'Derril', 'photo': '1'},
               {'official_name': 'YiFei Zhu', 'nick_name': 'YiFei', 'photo': '2'},
               {'official_name': 'Frank Lee', 'nick_name': 'Frank', 'photo': '3'},
               {'official_name': 'Ichiro Tai', 'nick_name': 'Derril', 'photo': '1'},
               {'official_name': 'YiFei Zhu', 'nick_name': 'YiFei', 'photo': '2'},
               {'official_name': 'Frank Lee', 'nick_name': 'Frank', 'photo': '3'},
               {'official_name': 'Ichiro Tai', 'nick_name': 'Derril', 'photo': '1'},
               {'official_name': 'YiFei Zhu', 'nick_name': 'YiFei', 'photo': '2'},
               {'official_name': 'Frank Lee', 'nick_name': 'Frank', 'photo': '3'}]
    return render_template('newleader.html',
                           title='New Leader',
                           user=user,
                           leader=leader,
                           members=members)


@clubblueprint.route('/inputatten')
def inputatten():
    '''Input Attendance'''
    user = ''
    club = 'Website Club'
    members = [{'official_name': 'Ichiro Tai', 'nick_name': 'Derril', 'photo': '1'},
               {'official_name': 'YiFei Zhu', 'nick_name': 'YiFei', 'photo': '2'},
               {'official_name': 'Frank Lee', 'nick_name': 'Frank', 'photo': '3'},
               {'official_name': 'Ichiro Tai', 'nick_name': 'Derril', 'photo': '1'},
               {'official_name': 'YiFei Zhu', 'nick_name': 'YiFei', 'photo': '2'},
               {'official_name': 'Frank Lee', 'nick_name': 'Frank', 'photo': '3'},
               {'official_name': 'Ichiro Tai', 'nick_name': 'Derril', 'photo': '1'},
               {'official_name': 'YiFei Zhu', 'nick_name': 'YiFei', 'photo': '2'},
               {'official_name': 'Frank Lee', 'nick_name': 'Frank', 'photo': '3'},
               {'official_name': 'Ichiro Tai', 'nick_name': 'Derril', 'photo': '1'},
               {'official_name': 'YiFei Zhu', 'nick_name': 'YiFei', 'photo': '2'},
               {'official_name': 'Frank Lee', 'nick_name': 'Frank', 'photo': '3'},
               {'official_name': 'Ichiro Tai', 'nick_name': 'Derril', 'photo': '1'},
               {'official_name': 'YiFei Zhu', 'nick_name': 'YiFei', 'photo': '2'},
               {'official_name': 'Frank Lee', 'nick_name': 'Frank', 'photo': '3'}]
    return render_template('inputatten.html',
                           title='Input Attendance',
                           user=user,
                           club=club,
                           members=members)


@clubblueprint.route('/memberinfo')
def memberinfo():
    '''Check Members' Info'''
    user = ''
    club = 'Website Club'
    members = [{'nick_name': 'Derril', 'id': 'G1234567890', 'official_name': 'Ichiro Tai', 'email': 'lolol@outlook.com'},
               {'nick_name': 'Derril', 'id': 'G1234567890', 'official_name': 'Ichiro Tai', 'email': 'lolol@outlook.com'},
               {'nick_name': 'Derril', 'id': 'G1234567890', 'official_name': 'Ichiro Tai', 'email': 'lolol@outlook.com'},
               {'nick_name': 'Derril', 'id': 'G1234567890', 'official_name': 'Ichiro Tai', 'email': 'lolol@outlook.com'},
               {'nick_name': 'Derril', 'id': 'G1234567890', 'official_name': 'Ichiro Tai', 'email': 'lolol@outlook.com'},
               {'nick_name': 'Derril', 'id': 'G1234567890', 'official_name': 'Ichiro Tai', 'email': 'lolol@outlook.com'},
               {'nick_name': 'Derril', 'id': 'G1234567890', 'official_name': 'Ichiro Tai', 'email': 'lolol@outlook.com'},
               {'nick_name': 'Derril', 'id': 'G1234567890', 'official_name': 'Ichiro Tai', 'email': 'lolol@outlook.com'}]
    return render_template('memberinfo.html',
                           title='Member Info',
                           user=user,
                           club=club,
                           members=members)


@clubblueprint.route('/changeclubinfo')
def changeclubinfo():
    '''Change Club's Info'''
    user = ''
    club = 'Website Club'
    one = 'We create oClubs for SHSID clubs.'
    quote = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
    person = 'Lorem'
    photo = 'intro5'
    intro = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
    return render_template('changeclubinfo.html',
                           title='Change Club Info',
                           user=user,
                           club=club,
                           one=one,
                           quote=quote,
                           person=person,
                           photo=photo,
                           intro=intro)


@clubblueprint.route('/adjust')
def adjustmember():
    '''Adjust Club Members'''
    user = ''
    club = 'Website Club'
    members = [{'nick_name': 'Derril', 'official_name': 'Ichiro Tai', 'photo': '1', 'id': 'G1234567890'},
               {'nick_name': 'Derril', 'official_name': 'Ichiro Tai', 'photo': '1', 'id': 'G1234567890'},
               {'nick_name': 'Derril', 'official_name': 'Ichiro Tai', 'photo': '1', 'id': 'G1234567890'},
               {'nick_name': 'Derril', 'official_name': 'Ichiro Tai', 'photo': '1', 'id': 'G1234567890'},
               {'nick_name': 'Derril', 'official_name': 'Ichiro Tai', 'photo': '1', 'id': 'G1234567890'},
               {'nick_name': 'Derril', 'official_name': 'Ichiro Tai', 'photo': '1', 'id': 'G1234567890'},
               {'nick_name': 'Derril', 'official_name': 'Ichiro Tai', 'photo': '1', 'id': 'G1234567890'},
               {'nick_name': 'Derril', 'official_name': 'Ichiro Tai', 'photo': '1', 'id': 'G1234567890'},
               {'nick_name': 'Derril', 'official_name': 'Ichiro Tai', 'photo': '1', 'id': 'G1234567890'},
               {'nick_name': 'Derril', 'official_name': 'Ichiro Tai', 'photo': '1', 'id': 'G1234567890'},
               {'nick_name': 'Derril', 'official_name': 'Ichiro Tai', 'photo': '1', 'id': 'G1234567890'}]
    return render_template('adjustmember.html',
                           title='Adjust Members',
                           user=user,
                           club=club,
                           members=members)
