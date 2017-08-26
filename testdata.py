#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals, division

from datetime import date, timedelta

from oclubs.objs import FormattedText, Activity, Club, User, Upload
from oclubs.enums import ActivityTime, ClubType, UserType, ClubJoinMode

from oclubs.app import app

from oclubs.access import done

week = timedelta(days=7)

with app.app_context():
    unpriv = User.new()
    unpriv.studentid = 'U0'
    unpriv.passportname = 'unpriv'
    unpriv.password = '123456'
    unpriv.nickname = 'unpriv'
    unpriv.email = 'unpriv@example.com'
    unpriv.phone = None
    unpriv.picture = Upload(-1)
    unpriv.type = UserType.STUDENT
    unpriv.grade = 12
    unpriv.currentclass = 20
    unpriv.create()

    yifei = User.new()
    yifei.studentid = 'A1'
    yifei.passportname = 'YiFei'
    yifei.password = '123456'
    yifei.nickname = 'YiFei'
    yifei.email = 'yifei@example.com'
    yifei.phone = None
    yifei.picture = Upload(-1)
    yifei.type = UserType.ADMIN
    yifei.grade = 12
    yifei.currentclass = 4
    yifei.create()

    derril = User.new()
    derril.studentid = 'A2'
    derril.passportname = 'Ichiro'
    derril.password = '123456'
    derril.nickname = 'Derril'
    derril.email = 'derril@example.com'
    derril.phone = 18909090909
    derril.picture = Upload(-1)
    derril.type = UserType.ADMIN
    derril.grade = 12
    derril.currentclass = 1
    derril.create()

    frank = User.new()
    frank.studentid = 'A3'
    frank.passportname = 'Frank'
    frank.password = '123456'
    frank.nickname = 'Frank'
    frank.email = 'frank@example.com'
    frank.phone = 12345678901
    frank.picture = Upload(-1)
    frank.type = UserType.ADMIN
    frank.grade = 12
    frank.currentclass = 1
    frank.create()

    mkc = User.new()
    mkc.studentid = 'A4'
    mkc.passportname = 'Ma Kai Chen'
    mkc.password = '123456'
    mkc.nickname = 'MKC'
    mkc.email = 'mkc@shsid.org'
    mkc.phone = 12345678901
    mkc.picture = Upload(-1)
    mkc.type = UserType.ADMIN
    mkc.grade = None
    mkc.currentclass = None
    mkc.create()

    lawerence = User.new()
    lawerence.studentid = 'S1'
    lawerence.passportname = 'Lan Hai'
    lawerence.password = '123456'
    lawerence.nickname = 'Lawerence'
    lawerence.email = 'lawerence@example.com'
    lawerence.phone = 12345678901
    lawerence.picture = Upload(-1)
    lawerence.type = UserType.STUDENT
    lawerence.grade = 13
    lawerence.currentclass = 9
    lawerence.create()

    stella = User.new()
    stella.studentid = 'T1'
    stella.passportname = 'Chen Qin'
    stella.password = '123456'
    stella.nickname = 'Stella'
    stella.email = 'stella@shsid.org'
    stella.phone = 12345678901
    stella.picture = Upload(-1)
    stella.type = UserType.TEACHER
    stella.grade = None
    stella.currentclass = None
    stella.create()

    sciexpclub = Club.new()
    sciexpclub.name = 'Science Experiment Club'
    sciexpclub.teacher = stella
    sciexpclub.leader = lawerence
    sciexpclub.description = FormattedText.emptytext()
    sciexpclub.location = 'XMT 201'
    sciexpclub.is_active = True
    sciexpclub.intro = 'We do experiments.'
    sciexpclub.picture = Upload(-1)
    sciexpclub.type = ClubType.ACADEMICS
    sciexpclub.joinmode = ClubJoinMode.FREE_JOIN
    sciexpclub.reactivate = True
    sciexpclub.create()

    sciexpclub.description = FormattedText.handle(lawerence, sciexpclub, 'We do **awesome** experiments')

    sciexpclub.add_member(yifei)
    sciexpclub.add_member(lawerence)
    sciexpclub.add_member(unpriv)

    for i in range(10):
        act = Activity.new()
        act.name = 'Exp'
        act.club = sciexpclub
        act.description = FormattedText.handle(lawerence, sciexpclub, '**Another** experiment')
        act.date = date(2016, 9, 2) + week * i
        act.time = ActivityTime.AFTERSCHOOL
        act.location = 'YFB'
        act.cas = 1
        act.post = FormattedText.emptytext()
        act.selections = []
        act.create()

    oliver = User.new()
    oliver.studentid = 'S2'
    oliver.passportname = 'Liang Zheng'
    oliver.password = '123456'
    oliver.nickname = 'Oliver'
    oliver.email = 'oliver@example.com'
    oliver.phone = 12345678901
    oliver.picture = Upload(-1)
    oliver.type = UserType.STUDENT
    oliver.grade = 12
    oliver.currentclass = 6
    oliver.create()

    yangbi = User.new()
    yangbi.studentid = 'T2'
    yangbi.passportname = 'Yang Bi'
    yangbi.password = '123456'
    yangbi.nickname = 'Yang Bi'
    yangbi.email = 'yangbi@shsid.org'
    yangbi.phone = 12345678901
    yangbi.picture = Upload(-1)
    yangbi.type = UserType.TEACHER
    yangbi.grade = None
    yangbi.currentclass = None
    yangbi.create()

    chemexpclub = Club.new()
    chemexpclub.name = 'Chemistry Experiment Club'
    chemexpclub.teacher = yangbi
    chemexpclub.leader = oliver
    chemexpclub.description = FormattedText.emptytext()
    chemexpclub.location = 'YFB'
    chemexpclub.is_active = True
    chemexpclub.intro = 'We do experiments.'
    chemexpclub.picture = Upload(-1)
    chemexpclub.type = ClubType.ACADEMICS
    chemexpclub.joinmode = ClubJoinMode.FREE_JOIN
    chemexpclub.reactivate = True
    chemexpclub.create()

    chemexpclub.add_member(yifei)
    chemexpclub.add_member(oliver)

    for i in range(10):
        act = Activity.new()
        act.name = 'Chem'
        act.club = chemexpclub
        act.description = FormattedText.emptytext()
        act.date = date(2016, 9, 3) + week * i
        act.time = ActivityTime.AFTERSCHOOL
        act.location = 'YFB'
        act.cas = 1
        act.post = FormattedText.emptytext()
        act.selections = []
        act.create()


    act = Activity.new()
    act.name = 'HongMei'
    act.club = chemexpclub
    act.description = FormattedText.emptytext()
    act.date = date(2016, 10, 20)
    act.time = ActivityTime.HONGMEI
    act.location = 'HongMei'
    act.cas = 5
    act.post = FormattedText.emptytext()
    act.selections = []
    act.create()


    jackson = User.new()
    jackson.studentid = 'S3'
    jackson.passportname = 'Jackson'
    jackson.password = '123456'
    jackson.nickname = 'Jackson'
    jackson.email = 'jackson@example.com'
    jackson.phone = 12345678901
    jackson.picture = Upload(-1)
    jackson.type = UserType.STUDENT
    jackson.grade = 12
    jackson.currentclass = 1
    jackson.create()

    yuhua = User.new()
    yuhua.studentid = 'T3'
    yuhua.passportname = 'Yu Hua'
    yuhua.password = '123456'
    yuhua.nickname = 'Drinking'
    yuhua.email = 'yuhua@shsid.org'
    yuhua.phone = 12345678901
    yuhua.picture = Upload(-1)
    yuhua.type = UserType.TEACHER
    yuhua.grade = None
    yuhua.currentclass = None
    yuhua.create()

    chessclub = Club.new()
    chessclub.name = 'Chess Club'
    chessclub.teacher = yuhua
    chessclub.leader = jackson
    chessclub.description = FormattedText.emptytext()
    chessclub.location = 'XMT 310'
    chessclub.is_active = True
    chessclub.intro = 'Chess is fun.'
    chessclub.picture = Upload(-1)
    chessclub.type = ClubType.ENTERTAINMENT
    chessclub.joinmode = ClubJoinMode.FREE_JOIN
    chessclub.reactivate = True
    chessclub.create()

    chessclub.add_member(yifei)
    chessclub.add_member(jackson)
    chessclub.add_member(unpriv)


    for i in range(10):
        act = Activity.new()
        act.name = 'Chess time'
        act.club = chessclub
        act.description = FormattedText.emptytext()
        act.date = date(2016, 9, 4) + week * i
        act.time = ActivityTime.NOON
        act.location = 'YFB'
        act.cas = 40/60
        act.post = FormattedText.emptytext()
        act.selections = []
        act.create()

    act = Activity.new()
    act.name = 'HongMei'
    act.club = chessclub
    act.description = FormattedText.emptytext()
    act.date = date(2016, 11, 20)
    act.time = ActivityTime.HONGMEI
    act.location = 'HongMei'
    act.cas = 5
    act.post = FormattedText.emptytext()
    act.selections = []
    act.create()

    __import__('code').interact("Check and do done()",
                                local=locals())
