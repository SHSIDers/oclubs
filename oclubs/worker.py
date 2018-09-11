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

from oclubs.access import done, database, elasticsearch, redis
from oclubs.access.redis import r_url_celery
from oclubs.app import app as flask_app
from oclubs.enums import UserType
from oclubs.objs import Activity, Club, User, Upload
from oclubs.objs.base import Property

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
        # DISABLED due to admin unable to fetch new account passwords
        # 'refresh_user_holiday_weekend_night': {
        #     'task': 'oclubs.worker.refresh_user',
        #     'schedule': crontab(minute=23, hour=2, day_of_week='sunday',
        #                         month_of_year='1,2,7,8'),
        # },
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

# This part does not work anymore, do not use this

# @app.task()
# @handle_app_context
# def refresh_user(authority):
#     ours = database.fetch_multirow(
#         'user',
#         {
#             'user_login_name': 'sid',
#             'user_id': 'uid',
#         },
#         [
#             ('!=', 'user_password', None),
#             ('=', 'user_type', UserType.STUDENT.value)
#         ]
#     )
#     ours = {data['sid']: data['uid'] for data in ours}
#
#     union = set(ours).union(authority)
#
#     for sid in union:
#         if sid in authority:
#             if sid in ours:
#                 _update_account.delay(ours[sid], authority[sid])
#             else:
#                 _create_account.delay(authority[sid])
#         else:
#             if sid in ours:
#                 _disable_account.delay(ours[sid])
#             else:
#                 assert False  # This is an impossibility


@app.task()
@handle_app_context
def _disable_account(uid):
    u = User(uid)
    u.password = None
    u.grade = None
    u.currentclass = None
    print 'DISABLED USER ID %d' % u.id


def _user_refresh(u, authority):
    u.studentid = authority['UNIONID']
    u.passportname = authority['NAMEEN']
    if 'GRADENAME' in authority:
        u.grade = int(authority['GRADENAME'])
    if 'STUCLASSNAME' in authority:
        u.currentclass = int(authority['STUCLASSNAME'])
    if 'EMAILADDRESS' in authority:
        u.email = authority['EMAILADDRESS']


@app.task()
@handle_app_context
def _create_account(authority, _type='STUDENT', haspassword=True):
    u = User.new()
    u.studentid = ''
    u.passportname = ''
    u.email = ''
    u.phone = None
    u.grade = None
    u.currentclass = None
    u.initalized = False
    _user_refresh(u, authority)
    password = User.generate_password() if haspassword else None
    u.password = password
    u.nickname = u.passportname
    u.picture = Upload(-1)
    u.type = UserType[_type]
    u.create(True)

    if haspassword:
        redis.RedisCache('tempuserpw:' + str(u.id), 3600 * 48).set(password)

    print 'CREATED USER ID %d' % u.id


@app.task()
@handle_app_context
def _update_account(uid, authority):
    u = User(uid)
    _user_refresh(u, authority)
    print 'UPDATED USER ID %d' % u.id


@app.task()
@handle_app_context
def rebuild_elasticsearch():
    types = {
        Club: {
            'conds': [('=', 'club_inactive', False)]
        },
        Activity: {}
    }
    for cls, params in types.items():
        db_ids = database.fetch_onecol(
            cls.table,
            cls.identifier,
            params.get('conds', [])
        )
        db_ids = set(int(x) for x in db_ids)
        if db_ids:
            db_max = max(db_ids)
        else:
            db_max = 0

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
