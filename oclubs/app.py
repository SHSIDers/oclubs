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


@app.errorhandler(Exception)
def exception_handler(e):
    '''Handle an exception and show the traceback'''
    try:
        pass
    except:
        return traceback.format_exc()


def login():
    '''Attempt to Login'''
    if 'user_id' in session:
        return True
    username = request.form['username']
    password = request.form['password']
    user = oclubs.objs.User.attempt_login(username, password)
    if user is not None:
        session['user_id'] = user.id
        return user
    else:
        return


@app.route('/', methods=['GET', 'POST'])
def homepage():
    '''Homepage'''
    if request.method == 'GET':
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
    if request.method == 'POST':
        if request.form['submist'] == 'Login':
            user = login()
            if user is None:
                # Show error message
                return jsonify()
            else:
                return redirect(url_for('homepage'))


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
