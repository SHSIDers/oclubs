#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import

from flask import (
    Flask, redirect, request, render_template, url_for, session, jsonify
)

import traceback

import oclubs
from oclubs.userblueprint import userblueprint
from oclubs.clubblueprint import clubblueprint
from oclubs.actblueprint import actblueprint

app = Flask(__name__)

app.register_blueprint(userblueprint, url_prefix='/user')
app.register_blueprint(clubblueprint, url_prefix='/club')
app.register_blueprint(actblueprint, url_prefix='/act')


@app.errorhandler(404)
@app.route('/404')
def wrong_url():
    if 'user_id' in session:
        user = oclubs.objs.User(session['user_id']).nickname
    else:
        user = ''
    return render_template('wrongurl.html',
                           title='Wrong URL',
                           user=user
                           ), 404


@app.errorhandler(403)
def no_access():
    user_obj = oclubs.objs.User(session['user_id'])
    return render_template('noaccess.html',
                           title='No Access',
                           user=user_obj.nickname
                           ), 403


@app.errorhandler(401)
def not_logged_in():
    return render_template('notloggedin.html',
                           title='Not Logged In',
                           user=''
                           ), 401


@app.route('/login', methods=['POST'])
def login():
    '''API to login'''
    if 'user_id' in session:
        status = 'loggedin'
    else:
        user = oclubs.objs.User.attempt_login(
            request.form['username'],
            request.form['password']
        )
        if user is not None:
            session['user_id'] = user.id
            status = 'success'
        else:
            status = 'failure'
    return jsonify({'result': status})


@app.route('/')
def homepage():
    '''Homepage'''
    if('user_id' in session):
        user = oclubs.objs.User(session['user_id'])
    else:
        user = ''
    # Three excellent clubs
    ex_clubs = [{'name': 'Website Club', 'picture': '1', 'intro': 'We create platform for SHSID.'},
                {'name': 'Art Club', 'picture': '2', 'intro': 'We invite people to the world of arts.'},
                {'name': 'Photo Club', 'picture': '3', 'intro': 'We search for the beauty in this world.'}]
    return render_template('homepage.html',
                           title='Here you come',
                           is_home=True,
                           user=user,
                           ex_clubs=ex_clubs)


@app.route('/about')
def about():
    '''About This Website'''
    if('user_id' in session):
        user = oclubs.objs.User(session['user_id']).nickname
    else:
        user = ''
    return render_template('about.html',
                           title='About',
                           is_about=True,
                           user=user)


@app.route('/advice')
def advice():
    '''Advice Page'''
    if('user_id' in session):
        user = oclubs.objs.User(session['user_id']).nickname
    else:
        user = ''
    return render_template('advice.html',
                           title='Advice',
                           user=user)


@app.route('/creators')
def creators():
    '''Introduction Page about Us'''
    if('user_id' in session):
        user = oclubs.objs.User(session['user_id']).nickname
    else:
        user = ''
    return render_template('creators.html',
                           title='Creators',
                           user=user)


if __name__ == '__main__':
    app.run()
