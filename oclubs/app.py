#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals, division


import traceback
import os
import math

from flask import (
    Flask, redirect, request, render_template, url_for, session, jsonify, g, abort, flash, Markup
)
from flask_login import LoginManager, login_user, logout_user, current_user

from oclubs.objs import User, Club, Activity, Upload
from oclubs.access import done as db_done, get_secret
from oclubs.userblueprint import userblueprint
from oclubs.clubblueprint import clubblueprint
from oclubs.actblueprint import actblueprint
from oclubs.enums import UserType, ClubType, ActivityTime
from oclubs.exceptions import NoRow

from oclubs.redissession import RedisSessionInterface
from oclubs.shared import encrypt, Pagination

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


def url_for_other_page(page):
    args = request.view_args.copy()
    args.update(request.args)
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page


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
    return render_template('static/error.html',
                           title='404 Page Not Found',
                           is_page_not_found=True
                           ), 404


@app.errorhandler(403)
@app.route('/403')  # debugger
def forbidden(e=None):
    '''No access'''
    return render_template('static/error.html',
                           title='403 Forbidden',
                           is_forbidden=True
                           ), 403


@app.errorhandler(401)
@app.route('/401')  # debugger
def unauthorized(e=None):
    '''Not logged in'''
    return render_template('static/error.html',
                           title='401 Unauthorized',
                           is_unauthorized=True
                           ), 401


@app.errorhandler(500)
@app.route('/500')  # debugger
def internal_server_error(e=None):
    '''Internal server error'''
    flash(encrypt(traceback.format_exc()), '500')
    return render_template('static/error.html',
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
    return render_template('user/login.html',
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
    search_type = request.args.get('search_type', 'club')
    keywords = request.args.get('keywords', '')
    page = int(request.args.get('page', 1))

    if search_type == 'club':
        cls, title, desc, pic, extras = (
            Club, 'name', ['intro', 'description'], lambda obj: obj.picture,
            [])
    else:
        cls, title, desc, pic, extras = (
            Activity, 'name', ['description', 'post'],
            lambda obj: obj.pictures[0] if obj.pictures else None,
            [('date', lambda obj: obj.date.isoformat())])

    search_result = cls.search(keywords, offset=(page-1)*10, size=10)

    results = []
    for result in search_result['results']:
        obj = result['object']
        highlight = result['highlight']

        try:
            resultdict = {
                'obj': obj,
                'name': _search_hl_or_attr(obj, highlight, [title]),
                'desc': _search_hl_or_attr(obj, highlight, desc),
                'pic': pic(obj)
            }
            for key, func in extras:
                resultdict[key] = func(obj)

            results.append(resultdict)
        except NoRow:  # database unsyncronized
            continue

    pagination = Pagination(page, 10, search_result['count'])

    return render_template('static/search.html',
                           title='Search',
                           search_result=search_result,
                           results=results,
                           keywords=keywords,
                           search_type=search_type,
                           pagination=pagination)


def _search_hl_or_attr(obj, highlight, namelist):
    markup = []
    for name in namelist:
        if name in highlight:
            markup.extend(highlight[name])
        else:
            text = _search_gettext(obj, name)
            if text:
                markup.append(text)

    return Markup('... ').join(markup)


def _search_gettext(obj, name):
    obj = getattr(obj, name)

    try:
        obj = obj.raw
    except AttributeError:
        pass

    try:
        return obj[:256]
    except TypeError:
        return obj


@app.route('/')
def homepage():
    '''Homepage'''
    top_pic = []
    col = []
    count = 0
    for act in Activity.get_activities_conditions(require_photos=True,
                                                  limit=(0, 12)):
        if count % 3 != 0:
            col.append(act)
            count += 1
        else:
            top_pic.append(col)
            col = []
    if count < 3:
        top_pic.append(col)
    ex_clubs = Club.excellentclubs(3)
    pic_acts = []
    for act in Activity.get_activities_conditions(require_photos=True,
                                                  limit=(0, 3)):
        pic_acts.append(act)
    return render_template('static/homepage.html',
                           title='Here you come',
                           is_home=True,
                           top_pic=top_pic,
                           ex_clubs=ex_clubs,
                           pic_acts=pic_acts)


@app.route('/about')
def about():
    '''About This Website'''
    return render_template('static/about.html',
                           title='About',
                           is_about=True)


@app.route('/advice')
def advice():
    '''Advice Page'''
    return render_template('static/advice.html',
                           title='Advice')


@app.route('/creators')
def creators():
    '''Introduction Page about Us'''
    return render_template('static/creators.html',
                           title='Creators')


if __name__ == '__main__':
    app.run()
