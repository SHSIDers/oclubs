#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

import celery
import pystache

from oclubs.access import done
from oclubs.access.redis import r_url_celery
from oclubs.app import app as flask_app
from oclubs.enums import UserType
from oclubs.objs import User, Upload

app = celery.Celery(
    'oclubsbackend',
    backend=r_url_celery + '1',
    broker=r_url_celery + '2'
)

app.conf.CELERY_TASK_RESULT_EXPIRES = 30 * 24 * 3600


@app.task(bind=True)
def create_user(self, stidentid, passportname, email):
    with flask_app.app_context():
        u = User.new()
        u.studentid = stidentid
        u.passportname = passportname
        u.email = email
        password = User.generate_password()
        u.password = password
        u.nickname = stidentid
        u.phone = None
        u.picture = Upload(-1)
        u.type = UserType.STUDENT
        u.gradyear = None
        u.create()

        # FIXME
        # with open('/srv/oclubs/email_templates/newuser', 'r') as textfile:
        #     data = textfile.read()
        # parameters = {'user': u}
        # contents = pystache.render(data, parameters)
        # u.email_user('Your Account', contents)

        print 'EMAIL USER ID %d NAME %s WITH PASSWORD %s' % (u.id, u.passportname, password)

        done()
