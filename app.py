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
    clubs = [{'name': 'art club', 'photo': 'intro1'},
             {'name': 'photo club', 'photo': 'intro2'},
             {'name': 'art club', 'photo': 'intro3'},
             {'name': 'photo club', 'photo': 'intro3'},
             {'name': 'art club', 'photo': 'intro4'},
             {'name': 'photo club', 'photo': 'intro5'},
             {'name': 'art club', 'photo': 'intro6'},
             {'name': 'photo club', 'photo': 'intro7'},
             {'name': 'art club', 'photo': 'intro8'},
             {'name': 'photo club', 'photo': 'intro9'}]
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
    top = {'image': 'picture', 'actname': 'Making Website', 'club': 'Website Club'}
    photos = [{'image1': 'intro1', 'actname1': 'Random Activity', 'club1': 'Random Club', 'image2': 'intro2', 'actname2': 'Random Activity', 'club2': 'Random Club'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'club1': 'Random Club', 'image2': 'intro2', 'actname2': 'Random Activity', 'club2': 'Random Club'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'club1': 'Random Club', 'image2': 'intro2', 'actname2': 'Random Activity', 'club2': 'Random Club'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'club1': 'Random Club', 'image2': 'intro2', 'actname2': 'Random Activity', 'club2': 'Random Club'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'club1': 'Random Club', 'image2': 'intro2', 'actname2': 'Random Activity', 'club2': 'Random Club'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'club1': 'Random Club', 'image2': 'intro2', 'actname2': 'Random Activity', 'club2': 'Random Club'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'club1': 'Random Club', 'image2': 'intro2', 'actname2': 'Random Activity', 'club2': 'Random Club'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'club1': 'Random Club', 'image2': 'intro2', 'actname2': 'Random Activity', 'club2': 'Random Club'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'club1': 'Random Club', 'image2': 'intro2', 'actname2': 'Random Activity', 'club2': 'Random Club'},
              {'image1': 'intro1', 'actname1': 'Random Activity', 'club1': 'Random Club', 'image2': 'intro2', 'actname2': 'Random Activity', 'club2': 'Random Club'}]
    return render_template('photos.html',
                           title='All Photos',
                           loggedin=loggedin,
                           top=top,
                           photos=photos)


def login():
    '''Attempt to login'''
    return


@app.route('/about')
def about():
    '''About This Website'''
    loggedin = False
    return render_template('about.html',
                           title='About',
                           loggedin=loggedin)

if __name__ == '__main__':
    app.run()
