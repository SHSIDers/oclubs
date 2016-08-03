#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

import celery

from oclubs.access import done
from oclubs.access.redis import r_url_celery
from oclubs.app import app as flask_app
from oclubs.enums import UserType
from oclubs.objs import User, Upload
from oclubs.shared import render_email_template

app = celery.Celery(
    'oclubsbackend',
    backend=r_url_celery + '1',
    broker=r_url_celery + '2'
)

app.conf.CELERY_TASK_RESULT_EXPIRES = 30 * 24 * 3600


@app.task(bind=True)
def refresh_user(self, studentid, passportname, grade, currentclass):
    with flask_app.app_context():
        u = User.new()
        u.studentid = studentid
        u.passportname = passportname
        u.email = None
        password = User.generate_password()
        u.password = password
        u.nickname = passportname
        u.phone = None
        u.picture = Upload(-1)
        u.type = UserType.STUDENT
        u.grade = None
        u.currentclass = None
        u.create()

        # FIXME
        # parameters = {'user': u}
        # contents = render_email_template('newuser', parameters)
        # u.email_user('Your Account', contents)

        print 'EMAIL USER ID %d NAME %s WITH PASSWORD %s' % (u.id, u.passportname, password)

        done()
