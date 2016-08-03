#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

from functools import wraps
import time

import celery
from celery.schedules import crontab
from elasticsearch.helpers import scan
from elasticsearch.exceptions import NotFoundError

from oclubs.access import done, database, db2, elasticsearch
from oclubs.access.redis import r_url_celery
from oclubs.app import app as flask_app
from oclubs.enums import UserType
from oclubs.objs import Activity, Club, User, Upload
from oclubs.objs.base import Property
from oclubs.shared import render_email_template

app = celery.Celery(
    'oclubsbackend',
    backend=r_url_celery + '1',
    broker=r_url_celery + '2'
)

app.conf.update(
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_TASK_RESULT_EXPIRES=30 * 24 * 3600,
    CELERY_TIMEZONE='Asia/Shanghai',
    CELERYBEAT_SCHEDULE={
        'rebuild_elasticsearch_night': {
            'task': 'oclubs.worker.rebuild_elasticsearch',
            'schedule': crontab(minute=47, hour=3),
        },
        'refresh_user_holiday_weekend_night': {
            'task': 'oclubs.worker.refresh_user',
            'schedule': crontab(minute=23, hour=2, day_of_week='sunday',
                                month_of_year='1,2,7,8'),
        },
    }
)


def handle_app_context(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        with flask_app.app_context():
            try:
                ret = func(*args, **kwargs)
                done(True)
                return ret
            except:
                done(False)
                raise

    return decorated_function


@app.task()
@handle_app_context
def refresh_user():
    authority = db2.allstudents()
    authority = {data['UNIONID']: data for data in authority}

    ours = database.fetch_multirow(
        'user',
        {
            'user_login_name': 'sid',
            'user_id': 'uid',
        },
        [
            ('!=', 'user_password', ''),
            ('=', 'user_type', UserType.STUDENT.value)
        ]
    )
    ours = {data['sid']: data['uid'] for data in ours}

    union = set(ours).union(authority)

    for sid in union:
        if sid in authority:
            if sid in ours:
                _refresh_user_update_account.delay(ours[sid], authority[sid])
            else:
                _refresh_user_create_account.delay(authority[sid])
        else:
            if sid in ours:
                _refresh_user_disable_account.delay(ours[sid])
            else:
                assert False  # This is an impossibility


@app.task()
@handle_app_context
def _refresh_user_disable_account(uid):
    u = User(uid)
    u.password = None
    u.grade = None
    u.currentclass = None
    print 'DISABLED USER ID %d' % u.id


def _refresh_user__refresh(u, authority):
    u.studentid = authority['UNIONID'].strip()
    u.passportname = authority['NAMEEN'].strip()
    u.grade = int(authority['GRADENAME'])
    u.currentclass = int(authority['STUCLASSNAME'])


@app.task()
@handle_app_context
def _refresh_user_create_account(authority):
    u = User.new()
    _refresh_user__refresh(u, authority)
    u.email = 'unknown@localhost'
    password = User.generate_password()
    u.password = password
    u.nickname = u.passportname
    u.phone = None
    u.picture = Upload(-1)
    u.type = UserType.STUDENT
    u.create()

    # FIXME
    # parameters = {'user': u}
    # contents = render_email_template('newuser', parameters)
    # u.email_user('Your Account', contents)
    print 'CREATED USER ID %d WITH PASSWORD %s' % (u.id, password)


@app.task()
@handle_app_context
def _refresh_user_update_account(uid, authority):
    u = User(uid)
    _refresh_user__refresh(u, authority)
    print 'UPDATED USER ID %d' % u.id


@app.task()
@handle_app_context
def rebuild_elasticsearch():
    for cls in [Activity, Club]:
        db_ids = database.fetch_onecol(
            cls.table,
            cls.identifier,
            {}
        )
        db_ids = set(int(x) for x in db_ids)
        db_max = max(db_ids)

        try:
            es_ids = scan(
                elasticsearch.es,
                index='oclubs',
                doc_type=cls.table,
                size=10000000,
                query={
                    'query': {'match_all': {}},
                    'size': 10000,
                    'fields': ['_id']
                })
            es_ids = (d['_id'] for d in es_ids)
            es_ids = set(int(x) for x in es_ids)
        except NotFoundError:
            es_ids = []

        if es_ids:
            es_max = max(es_ids)
        else:
            es_max = 0

        max_id = max(db_max, es_max)

        cls_searchprops = [
            prop.name for prop in [
                getattr(cls, propname) for propname in dir(cls)
            ] if isinstance(prop, Property) and prop.search
        ]

        for i in xrange(1, max_id + 1):
            time.sleep(0.01)

            if i in db_ids:
                obj = cls(i)

                db_data = {}
                for propname in cls_searchprops:
                    db_data[propname] = (
                        getattr(cls, propname).search(getattr(obj, propname)))

                if i in es_ids:
                    es_data = elasticsearch.get(cls.table, i)
                    if db_data == es_data:
                        print 'TYPE %s ID %d MATCH' % (cls.table, i)
                    else:
                        print 'UPDATED ES TYPE %s ID %d' % (cls.table, i)
                        elasticsearch.update(cls.table, i, db_data)
                else:
                    print 'CREATED ES TYPE %s ID %d' % (cls.table, i)
                    elasticsearch.create(cls.table, i, db_data)
            else:
                if i in es_ids:
                    print 'DELETED ES TYPE %s ID %d' % (cls.table, i)
                    elasticsearch.delete(cls.table, i)
                else:
                    print 'TYPE %s ID %d DOES NOT EXIST' % (cls.table, i)
                    pass
