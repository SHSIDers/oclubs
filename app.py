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
        clubactivities()
    except:
        return traceback.format_exc()


@app.route('/')
def home():
    '''Homepage'''
    loggedin = False
    return render_template('homepage.html',
                           title='Here you come',
                           loggedin=loggedin)


@app.route('/clublist')
def clublist():
    '''Club List'''
    loggedin = False
    clubs = [{'name': 'art club', 'photo': 'picture'},
             {'name': 'photo club', 'photo': 'picture'},
             {'name': 'art club', 'photo': 'picture'},
             {'name': 'photo club', 'photo': 'picture'},
             {'name': 'art club', 'photo': 'picture'},
             {'name': 'photo club', 'photo': 'picture'},
             {'name': 'art club', 'photo': 'picture'},
             {'name': 'photo club', 'photo': 'picture'},
             {'name': 'art club', 'photo': 'picture'},
             {'name': 'photo club', 'photo': 'picture'}]
    return render_template('clublist.html',
                           title='Club List',
                           loggedin=loggedin,
                           clubs=clubs)


@app.route('/clubintro')
def clubintro():
    '''Club Intro'''
    loggedin = False
    return render_template('clubintro.html',
                           title='Club Intro',
                           loggedin=loggedin)


@app.route('/allact')
def allactivities():
    '''All Activities'''
    loggedin = False
    activities = [{'club_name': 'Art Club', 'act_name': 'Painting', 'time': 'June 30, 2016', 'place': 'Art Center'},
                  {'club_name': 'Photo Club', 'act_name': 'Taking Pictures', 'time': 'June 30, 2016', 'place': 'SHSID Campus'},
                  {'club_name': 'Art Club', 'act_name': 'Painting', 'time': 'June 30, 2016', 'place': 'Art Center'},
                  {'club_name': 'Photo Club', 'act_name': 'Taking Pictures', 'time': 'June 30, 2016', 'place': 'SHSID Campus'},
                  {'club_name': 'Art Club', 'act_name': 'Painting', 'time': 'June 30, 2016', 'place': 'Art Center'},
                  {'club_name': 'Photo Club', 'act_name': 'Taking Pictures', 'time': 'June 30, 2016', 'place': 'SHSID Campus'},
                  {'club_name': 'Art Club', 'act_name': 'Painting', 'time': 'June 30, 2016', 'place': 'Art Center'},
                  {'club_name': 'Photo Club', 'act_name': 'Taking Pictures', 'time': 'June 30, 2016', 'place': 'SHSID Campus'},
                  {'club_name': 'Art Club', 'act_name': 'Painting', 'time': 'June 30, 2016', 'place': 'Art Center'},
                  {'club_name': 'Photo Club', 'act_name': 'Taking Pictures', 'time': 'June 30, 2016', 'place': 'SHSID Campus'},
                  {'club_name': 'Art Club', 'act_name': 'Painting', 'time': 'June 30, 2016', 'place': 'Art Center'},
                  {'club_name': 'Photo Club', 'act_name': 'Taking Pictures', 'time': 'June 30, 2016', 'place': 'SHSID Campus'}]
    return render_template('allact.html',
                           title='All Activities',
                           loggedin=loggedin,
                           activities=activities)


@app.route('/clubact')
def clubactivities():
    '''One Club's Activities'''
    loggedin = False
    club = {'image1': 'picture', 'image2': 'picture', 'image3': 'picture', 'club_name': 'Art Club'}
    activities = [{'act_name': 'Painting', 'time': 'June 30, 2016', 'place': 'Art Center'},
                  {'act_name': 'Taking Pictures', 'time': 'June 30, 2016', 'place': 'SHSID Campus'},
                  {'act_name': 'Painting', 'time': 'June 30, 2016', 'place': 'Art Center'},
                  {'act_name': 'Taking Pictures', 'time': 'June 30, 2016', 'place': 'SHSID Campus'},
                  {'act_name': 'Painting', 'time': 'June 30, 2016', 'place': 'Art Center'},
                  {'act_name': 'Taking Pictures', 'time': 'June 30, 2016', 'place': 'SHSID Campus'},
                  {'act_name': 'Painting', 'time': 'June 30, 2016', 'place': 'Art Center'},
                  {'act_name': 'Taking Pictures', 'time': 'June 30, 2016', 'place': 'SHSID Campus'},
                  {'act_name': 'Painting', 'time': 'June 30, 2016', 'place': 'Art Center'},
                  {'act_name': 'Taking Pictures', 'time': 'June 30, 2016', 'place': 'SHSID Campus'},
                  {'act_name': 'Painting', 'time': 'June 30, 2016', 'place': 'Art Center'},
                  {'act_name': 'Taking Pictures', 'time': 'June 30, 2016', 'place': 'SHSID Campus'}]
    return render_template('clubact.html',
                           title=club['club_name'],
                           loggedin=loggedin,
                           club=club,
                           activities=activities)


@app.route('/photos')
def allphotos():
    loggedin = False
    top = {'image1': 'picture', 'image1_actname': 'Making Website', 'image1_club': 'Website Club', 'image2': 'picture', 'image2_actname': 'Painting', 'image2_club': 'Art Club'}
    photos = [{'image': 'picture', 'actname': 'Random Activity', 'club': 'Random Club'},
              {'image': 'picture', 'actname': 'Random Activity', 'club': 'Random Club'},
              {'image': 'picture', 'actname': 'Random Activity', 'club': 'Random Club'},
              {'image': 'picture', 'actname': 'Random Activity', 'club': 'Random Club'},
              {'image': 'picture', 'actname': 'Random Activity', 'club': 'Random Club'},
              {'image': 'picture', 'actname': 'Random Activity', 'club': 'Random Club'},
              {'image': 'picture', 'actname': 'Random Activity', 'club': 'Random Club'},
              {'image': 'picture', 'actname': 'Random Activity', 'club': 'Random Club'},
              {'image': 'picture', 'actname': 'Random Activity', 'club': 'Random Club'},
              {'image': 'picture', 'actname': 'Random Activity', 'club': 'Random Club'},
              {'image': 'picture', 'actname': 'Random Activity', 'club': 'Random Club'},
              {'image': 'picture', 'actname': 'Random Activity', 'club': 'Random Club'},
              {'image': 'picture', 'actname': 'Random Activity', 'club': 'Random Club'},
              {'image': 'picture', 'actname': 'Random Activity', 'club': 'Random Club'},
              {'image': 'picture', 'actname': 'Random Activity', 'club': 'Random Club'}]
    return render_template('photos.html',
                           title='All Photos',
                           loggedin=loggedin,
                           top=top,
                           photos=photos)


def login():
    '''Attempt to login'''
    return


if __name__ == '__main__':
    app.run()
