#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from flask import (
    Blueprint, render_template, url_for, request
)

import traceback

userblueprint = Blueprint('userblueprint', __name__)


@userblueprint.route('/quit')
def quitclub():
    '''Quit Club Page'''
    user = ''
    clubs = ['Art Club', 'Photo Club', 'MUN', 'Art Club', 'Photo Club', 'MUN', 'Art Club', 'Photo Club', 'MUN']
    return render_template('quitclub.html',
                           title='Quit Club',
                           user=user,
                           clubs=clubs)


@userblueprint.route('/reghm')
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
        user = 'Derril'
        pictures = []
        for num in range(1, 21):
            pictures.append(num)
        info = {'name': 'Ichiro Tai', 'email': 'lolol@outlook.com', 'photo': '1', 'ID': 'G2986510295', 'phone': '18918181818'}
        clubs = [{'name': 'Website Club', 'photo': 'intro1', 'intro': 'We are the best club', 'cas': 110},
                 {'name': 'Math Club', 'photo': 'intro2', 'intro': 'We learn math together', 'cas': 5},
                 {'name': 'Chess Club', 'photo': 'intro3', 'intro': 'We enjoy playing chess', 'cas': 3}]
        evaluate = False
        castotal = 0
        for club in clubs:
            castotal += club['cas']
        activities = [{'club': 'Website Club', 'act': 'Create Club Platform', 'time': 'Forever', 'place': 'Home'},
                      {'club': 'Chess Club', 'act': 'Chess Tournament', 'time': 'June 1, 2011', 'place': 'XMT 201'},
                      {'club': 'Math Club', 'act': 'Do Math Homework', 'time': 'July 2, 2012', 'place': 'Home'}]
        hongmei = [{'club': 'Chess Club', 'act': 'Teach Basic Rules of Chess', 'time': 'March 2, 2012'},
                   {'club': 'Math Club', 'act': 'Teach Multiplication', 'time': 'March 9, 2012'}]
        leader_club = 'Website Club'
        return render_template('personal.html',
                               title=user,
                               user=user,
                               pictures=pictures,
                               info=info,
                               clubs=clubs,
                               evaluate=evaluate,
                               castotal=castotal,
                               activities=activities,
                               hongmei=hongmei,
                               leader_club=leader_club)


@userblueprint.route('/teacher')
def teacher():
    '''Teacher Page'''
    user = 'Derril'
    myclubs = [{'club': 'Website Club', 'members_num': 3, 'photo': '1', 'intro': 'We are the best club'},
               {'club': 'Math Club', 'members_num': 20, 'photo': '2', 'intro': 'We learn math together'}]
    pictures = []
    for num in range(1, 21):
        pictures.append(num)
    info = {'name': 'Ichiro Tai', 'email': 'lolol@outlook.com', 'photo': '1'}
    return render_template('teacher.html',
                           title=user,
                           user=user,
                           myclubs=myclubs,
                           pictures=pictures,
                           info=info)


@userblueprint.route('/forgotpw')
def forgotpw():
    '''Page for retrieving password'''
    user = ''
    return render_template('forgotpassword.html',
                           title='Retrieve Password',
                           user=user)
