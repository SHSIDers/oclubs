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

from oclubs.redissession import RedisSessionInterface

app = Flask(__name__)

app.register_blueprint(userblueprint, url_prefix='/user')
app.register_blueprint(clubblueprint, url_prefix='/club')
app.register_blueprint(actblueprint, url_prefix='/act')

app.session_interface = RedisSessionInterface()


def get_name():
    '''Get user's name if available'''
    if 'user_id' in session:
        user_obj = oclubs.objs.User(session['user_id'])
        user = user_obj.nickname
    else:
        user = ''
    return user


app.jinja_env.globals['usernickname'] = get_name


@app.errorhandler(404)
@app.route('/404')
def wrong_url(e):
    user = get_name()
    return render_template('wrongurl.html',
                           title='Wrong URL',
                           user=user
                           ), 404


@app.errorhandler(403)
def no_access(e):
    user_obj = oclubs.objs.User(session['user_id'])
    return render_template('noaccess.html',
                           title='No Access',
                           user=user_obj.nickname
                           ), 403


@app.errorhandler(401)
def not_logged_in(e):
    return render_template('notloggedin.html',
                           title='Not Logged In',
                           user=''
                           ), 401


@app.errorhandler(500)
def error(e):
    '''Internal server error'''
    user = get_name()
    return render_template('500.html',
                           title='Error',
                           user=user
                           ), 500


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
    user = get_name()
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
    user = get_name()
    return render_template('about.html',
                           title='About',
                           is_about=True,
                           user=user)


@app.route('/advice')
def advice():
    '''Advice Page'''
    user = get_name()
    return render_template('advice.html',
                           title='Advice',
                           user=user)


@app.route('/creators')
def creators():
    '''Introduction Page about Us'''
    user = get_name()
    return render_template('creators.html',
                           title='Creators',
                           user=user)


if __name__ == '__main__':
    app.run()
