#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Adapted from: http://flask.pocoo.org/snippets/75/ under Public Domain
#

"""Server side session on Redis."""

from datetime import timedelta
from uuid import uuid4
from flask.sessions import SessionInterface, SessionMixin

from oclubs.access.redis import RedisDict


class RedisSession(RedisDict, SessionMixin):
    def __new__(cls, prefix, sid):
        self = super(RedisDict, cls).__new__(cls, prefix + sid, 0)
        self.sid = sid
        return self

    def rollback(self):
        self.clear()
        self.update(self.unserialize(self._initial))


class RedisSessionInterface(SessionInterface):
    session_class = RedisSession

    def __init__(self, prefix='session:'):
        self.prefix = prefix

    def generate_sid(self):
        return str(uuid4())

    def get_redis_expiration_time(self, app, session):
        if session.permanent:
            return app.permanent_session_lifetime
        return timedelta(days=1)

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        sid = sid or self.generate_sid()
        session = self.session_class(self.prefix, sid)
        session.detach()  # prevent race condition
        return session

    def save_session(self, app, session, response):
        redis_exp = self.get_redis_expiration_time(app, session)
        session.timeout = int(redis_exp.total_seconds())
        session.save()

        domain = self.get_cookie_domain(app)
        if not session:
            if session.modified:
                response.delete_cookie(app.session_cookie_name,
                                       domain=domain)
        else:
            cookie_exp = self.get_expiration_time(app, session)
            response.set_cookie(app.session_cookie_name, session.sid,
                                expires=cookie_exp, httponly=True,
                                domain=domain)
