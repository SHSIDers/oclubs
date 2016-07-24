#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals


import traceback
import os

from flask import (
    Flask, redirect, request, render_template, url_for, session, jsonify, g, abort, flash, Markup
)
from flask_login import LoginManager, login_user, logout_user, current_user

from oclubs.objs import User, Club, Activity, Upload
from oclubs.access import done as db_done
from oclubs.userblueprint import userblueprint
from oclubs.clubblueprint import clubblueprint
from oclubs.actblueprint import actblueprint
from oclubs.enums import UserType, ClubType, ActivityTime

from oclubs.redissession import RedisSessionInterface
from oclubs.shared import get_secret, encrypt

app = Flask(__name__)

app.config['SECRET_KEY'] = get_secret('flask_key')

app.register_blueprint(userblueprint, url_prefix='/user')
app.register_blueprint(clubblueprint, url_prefix='/club')
app.register_blueprint(actblueprint, url_prefix='/act')

app.session_interface = RedisSessionInterface()

login_manager = LoginManager()
login_manager.init_app(app)


def get_picture(picture, ext='jpg'):
    return url_for('static', filename='images/' + picture + '.' + ext)

app.jinja_env.globals['getpicture'] = get_picture


@app.after_request
def access_done(response):
    if response.status_code < 400:
        db_done(True)
    else:
        db_done(False)
    return response


@app.teardown_appcontext
def access_teardown(exception):
    db_done(False)


@app.errorhandler(404)
@app.route('/404')  # debugger
def page_not_found(e=None):
    '''Wrong url'''
    return render_template('error.html',
                           title='404 Page Not Found',
                           is_page_not_found=True
                           ), 404


@app.errorhandler(403)
@app.route('/403')  # debugger
def forbidden(e=None):
    '''No access'''
    return render_template('error.html',
                           title='403 Forbidden',
                           is_forbidden=True
                           ), 403


@app.errorhandler(401)
@app.route('/401')  # debugger
def unauthorized(e=None):
    '''Not logged in'''
    return render_template('error.html',
                           title='401 Unauthorized',
                           is_unauthorized=True
                           ), 401


@app.errorhandler(500)
@app.route('/500')  # debugger
def internal_server_error(e=None):
    '''Internal server error'''
    flash(encrypt(traceback.format_exc()), '500')
    return render_template('error.html',
                           title='500 Internal Server Error',
                           is_internal_server_error=True
                           ), 500


@login_manager.user_loader
def load_user(user_id):
    try:
        user = User(int(user_id))
        assert user.nickname
        return user
    except Exception:
        return None


@app.route('/login')
def login():
    '''Login page'''
    return render_template('login.html',
                           title='Login')


@app.route('/login/submit', methods=['POST'])
def login_submit():
    '''API to login'''
    user = User.attempt_login(
        request.form['username'],
        request.form['password']
    )
    if user is not None:
        login_user(user, remember=('remember' in request.form))
    else:
        flash('Please enter your username and password correctly in order to login.', 'login')
        return redirect(url_for('login'))
    return redirect(url_for('userblueprint.personal'))


@app.route('/logout')
def logout():
    '''Logout a user'''
    logout_user()
    return redirect(url_for('homepage'))


@app.route('/search')
def search():
    '''Search Page'''
    try:
        search_type = request.args['search_type']
        keywords = request.args['keywords']
        if search_type == 'club':
            search = Club.search(keywords, offset=0, size=5)
        else:
            search = Activity.search(keywords, offset=0, size=5)
        count = str(search['count'])
        instead = ''
        if search['instead'] is not None:
            instead = search['instead']
        results = []
        for each_search in search['results']:
            result = {}
            obj = each_search['object']
            if search_type == 'club':
                result['picture'] = obj.picture
                result['name'] = obj.name
            else:
                if obj.pictures:
                    result['picture'] = obj.pictures[0]
                else:
                    result['picture'] = Upload(-1)  # FIXME: change to default picture
                result['name'] = obj.name
            highlight = each_search['highlight']
            highlight_result = []
            if 'name' in highlight:
                highlight_result.append(highlight['name'])
            if 'intro' in highlight:
                highlight_result.append(highlight['intro'])
            if 'description' in highlight:
                highlight_result.append(highlight['description'])
            result['highlight'] = Markup('...').join(highlight_result)
            results.append(result)
        return render_template('search.html',
                               title='Search',
                               count=count,
                               instead=instead,
                               results=results,
                               keywords=keywords,
                               search_type=search_type)
    except:
        traceback.print_exc()


@app.route('/')
def homepage():
    '''Homepage'''
    # Three excellent clubs
    ex_clubs = [{'name': 'Website Club', 'picture': '1', 'intro': 'We create platform for SHSID.'},
                {'name': 'Art Club', 'picture': '2', 'intro': 'We invite people to the world of arts.'},
                {'name': 'Photo Club', 'picture': '3', 'intro': 'We search for the beauty in this world.'}]
    return render_template('homepage.html',
                           title='Here you come',
                           is_home=True,
                           ex_clubs=ex_clubs)


@app.route('/about')
def about():
    '''About This Website'''
    return render_template('about.html',
                           title='About',
                           is_about=True)


@app.route('/advice')
def advice():
    '''Advice Page'''
    return render_template('advice.html',
                           title='Advice')


@app.route('/creators')
def creators():
    '''Introduction Page about Us'''
    return render_template('creators.html',
                           title='Creators')


if __name__ == '__main__':
    app.run()
