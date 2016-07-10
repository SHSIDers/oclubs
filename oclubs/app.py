#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from flask import (
    Flask, redirect, request, render_template, url_for
)

import traceback

from userblueprint import userblueprint
from clubblueprint import clubblueprint
from actblueprint import actblueprint

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


@app.route('/')
def home():
    '''Homepage'''
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
    user = ''
    return render_template('about.html',
                           title='About',
                           is_about=True,
                           user=user)


@app.route('/advice')
def advice():
    '''Advice Page'''
    user = ''
    return render_template('advice.html',
                           title='Advice',
                           user=user)


@app.route('/creators')
def creators():
    '''Introduction Page about Us'''
    user = ''
    return render_template('creators.html',
                           title='Creators',
                           user=user)


if __name__ == '__main__':
    app.run()
