#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from flask import (
    Flask, redirect, request, render_template, url_for
)

import traceback

app = Flask(__name__)

# Remember to use blueprint


@app.errorhandler(Exception)
def exception_handler(e):
    '''Handle an exception and show the traceback'''
    try:
        activity()
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


@app.route('/clublist')
def clublist():
    '''Club List'''
    user = ''
    clubs = [{'name': 'Art Club', 'photo': 'intro1', 'intro': 'Here is where birth of arts happens'},
             {'name': 'Photo Club', 'photo': 'intro2', 'intro': 'Place for photography!'},
             {'name': 'Art Club', 'photo': 'intro3', 'intro': 'Here is where birth of arts happens'},
             {'name': 'Photo Club', 'photo': 'intro3', 'intro': 'Place for photography!'},
             {'name': 'Art Club', 'photo': 'intro4', 'intro': 'Here is where birth of arts happens'},
             {'name': 'Photo Club', 'photo': 'intro5', 'intro': 'Place for photography!'},
             {'name': 'Art Club', 'photo': 'intro6', 'intro': 'Here is where birth of arts happens'},
             {'name': 'Photo Club', 'photo': 'intro7', 'intro': 'Place for photography!'},
             {'name': 'Art Club', 'photo': 'intro8', 'intro': 'Here is where birth of arts happens'},
             {'name': 'Photo Club', 'photo': 'intro9', 'intro': 'Place for photography!'}]
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
                           is_allact=True,
                           user=user,
                           activities=activities)


@app.route('/clubact')
def clubactivities():
    '''One Club's Activities'''
    user = ''
    club = {'image1': '1', 'image2': '2', 'image3': '3', 'club_name': 'Art Club'}
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
    top = {'image': 'intro5', 'actname': 'Making Website', 'club': 'Website Club'}
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


@app.route('/reghm')
def registerhm():
    '''Register Page for HongMei Activites'''
    user = ''
    club = 'Website Club'
    schedule = [{'id': '1', 'date': 'June 6 2016', 'activity': 'Finish homepage design'},
                {'id': '2', 'date': 'June 7 2016', 'activity': 'Finish activity page design'},
                {'id': '3', 'date': 'June 8 2016', 'activity': 'Finish personal page design'},
                {'id': '4', 'date': 'June 9 2016', 'activity': 'Finish club page design'},
                {'id': '5', 'date': 'June 10 2016', 'activity': 'Finish photo page design'},
                {'id': '6', 'date': 'June 11 2016', 'activity': 'Finish about page design'},
                {'id': '7', 'date': 'June 6 2016', 'activity': 'Finish homepage design'},
                {'id': '8', 'date': 'June 7 2016', 'activity': 'Finish activity page design'},
                {'id': '9', 'date': 'June 8 2016', 'activity': 'Finish personal page design'},
                {'id': '10', 'date': 'June 9 2016', 'activity': 'Finish club page design'},
                {'id': '11', 'date': 'June 10 2016', 'activity': 'Finish photo page design'},
                {'id': '12', 'date': 'June 11 2016', 'activity': 'Finish about page design'},
                {'id': '13', 'date': 'June 6 2016', 'activity': 'Finish homepage design'},
                {'id': '14', 'date': 'June 7 2016', 'activity': 'Finish activity page design'},
                {'id': '15', 'date': 'June 8 2016', 'activity': 'Finish personal page design'},
                {'id': '16', 'date': 'June 9 2016', 'activity': 'Finish club page design'},
                {'id': '17', 'date': 'June 10 2016', 'activity': 'Finish photo page design'},
                {'id': '18', 'date': 'June 11 2016', 'activity': 'Finish about page design'}]
    return render_template('registerhm.html',
                           title='Register for HongMei',
                           user=user,
                           club=club,
                           schedule=schedule)


@app.route('/act')
def activity():
    '''Club Activity Page'''
    user = ''
    activity = {'club': 'Website Club', 'actname': 'Making Website',
                'time': 'June 6 2016', 'people': '20-30', 'intro': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'}
    return render_template('activity.html',
                           title=activity['actname'],
                           user=user,
                           activity=activity)


if __name__ == '__main__':
    app.run()
