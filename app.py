# coding=gbk

#! /usr/bin/env python
# -*- coding: UTF-8 -*-

from flask import (
    Flask, redirect, request, render_template, url_for
)

import traceback

app = Flask(__name__)


@app.errorhandler(Exception)
def exception_handler(e):
    '''Handle an exception and show the traceback'''
    try:
        return render_template('clublist.html',
                               title='Here you come',
                               loggedin=False)
    except:
        return traceback.format_exc()


@app.route('/')
def home():
    '''Homepage'''
    loggedin = False
    return render_template('clublist.html',
                           title='Here you come',
                           loggedin=loggedin)


@app.route('/clublist')
def clublist():
    '''Club List'''
    loggedin = False
    clubs = [{'name': 'art_club', 'photo': 'picture'},
             {'name': 'photo_club', 'photo': 'picture'}]
    return render_template('clublist.html',
                           title='Club List',
                           loggedin=loggedin,
                           clubs=clubs)


def login():
    '''Attempt to login'''
    return


@app.route('/clubintro')
def clubintro():
    return render_template()

if __name__ == '__main__':
    app.run()
