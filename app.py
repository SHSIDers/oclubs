#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from flask import (
    Flask, redirect, request, render_template, url_for
)

import traceback

app = Flask(__name__)

#Remember to use blueprint


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
    user = ''
    '''Three excellent clubs'''
    ex_clubs = [{'name': 'Website Club', 'picture': '1', 'intro': 'We create platform for SHSID.'},
                {'name': 'Art Club', 'picture': '2', 'intro': 'We invite people to the world of arts.'},
                {'name': 'Photo Club', 'picture': '3', 'intro': 'We search for the beauty in this world.'}]
    return render_template('homepage.html',
                           title='Here you come',
                           is_home=True,
                           user=user,
                           ex_clubs=ex_clubs)


@app.route('/clublist')
def clublist():
    '''Club List'''
    user = ''
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
                           is_list=True,
                           user=user,
                           clubs=clubs)


@app.route('/clubintro')
def clubintro():
    '''Club Intro'''
    user = ''
    return render_template('clubintro.html',
                           title='Club Intro',
                           user=user)


@app.route('/allact')
def allactivities():
    '''All Activities'''
    user = ''
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
                           user=user,
                           activities=activities)


@app.route('/clubact')
def clubactivities():
    '''One Club's Activities'''
    user = ''
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
                           user=user,
                           club=club,
                           activities=activities)


@app.route('/photos')
def allphotos():
    user = ''
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
                           is_photos=True,
                           user=user,
                           top=top,
                           photos=photos)


def login():
    '''Attempt to login'''
    return


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


@app.route('/newleader')
def newleader():
    '''Selecting New Club Leader'''
    user = ''
    leader = {'official_name': 'Feng Ma', 'nick_name': 'Principal Ma', 'photo': '4'}
    members = [{'official_name': 'Ichiro Tai', 'nick_name': 'Derril', 'photo': '1'},
               {'official_name': 'YiFei Zhu', 'nick_name': 'YiFei', 'photo': '2'},
               {'official_name': 'Frank Lee', 'nick_name': 'Frank', 'photo': '3'},
               {'official_name': 'Ichiro Tai', 'nick_name': 'Derril', 'photo': '1'},
               {'official_name': 'YiFei Zhu', 'nick_name': 'YiFei', 'photo': '2'},
               {'official_name': 'Frank Lee', 'nick_name': 'Frank', 'photo': '3'},
               {'official_name': 'Ichiro Tai', 'nick_name': 'Derril', 'photo': '1'},
               {'official_name': 'YiFei Zhu', 'nick_name': 'YiFei', 'photo': '2'},
               {'official_name': 'Frank Lee', 'nick_name': 'Frank', 'photo': '3'},
               {'official_name': 'Ichiro Tai', 'nick_name': 'Derril', 'photo': '1'},
               {'official_name': 'YiFei Zhu', 'nick_name': 'YiFei', 'photo': '2'},
               {'official_name': 'Frank Lee', 'nick_name': 'Frank', 'photo': '3'},
               {'official_name': 'Ichiro Tai', 'nick_name': 'Derril', 'photo': '1'},
               {'official_name': 'YiFei Zhu', 'nick_name': 'YiFei', 'photo': '2'},
               {'official_name': 'Frank Lee', 'nick_name': 'Frank', 'photo': '3'}]
    return render_template('newleader.html',
                           title='New Leader',
                           user=user,
                           leader=leader,
                           members=members)


@app.route('/quit')
def quitclub():
    '''Quit Club Page'''
    user = ''
    clubs = ['Art Club', 'Photo Club', 'MUN', 'Art Club', 'Photo Club', 'MUN', 'Art Club', 'Photo Club', 'MUN']
    return render_template('quitclub.html',
                           title='Quit Club',
                           user=user,
                           clubs=clubs)


@app.route('/club')
def clubmanage():
    '''Club Management Page'''
    user = ''
    return render_template('club.html',
                           title='Club',
                           user=user)


@app.route('/newact')
def newact():
    '''Hosting New Activity'''
    user = ''
    return render_template('newact.html',
                           title='New Activity',
                           user=user)


if __name__ == '__main__':
    app.run()
