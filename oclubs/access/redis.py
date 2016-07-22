#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
from __future__ import absolute_import, unicode_literals

from redis import Redis
from Flask import g
import json

r = Redis(host='localhost', port=6379, db=0)
g.stuffList = {}


def done():
    for stuff in g.stuffList.values():
        stuff.save()


class RedisStuff(object):
    def load(self):
        self._initial = json.dumps(self)
        val = r.get(self.key)
        if val is None:
            return ()
        try:
            ret = json.loads(val)
        except ValueError:
            r.delete(self.key)
            return ()
        return ret

    def save(self, timeout=-1):
        if self._initial != json.dumps(self):
            r.set(self.key, json.dumps(self))
            if timeout == -1:
                r.persist(self.key)
            else:
                r.expire(self.key, timeout)
            return True
        return False


class RedisDict(dict, RedisStuff):
    def __init__(self, key):
        self.key = key
        g.stuffList[self.key] = self
        super(RedisDict, self).__init__(self.load())


class RedisList(list, RedisStuff):
    def __init__(self, key):
        self.key = key
        g.stuffList[self.key] = self
        super(RedisList, self).__init__(self.load())


class RedisCache(str):
    def __init__(self, key):
        self.key = key
        g.stuffList[self.key] = self
        super(RedisCache, self).__init__(self.load())

    def load(self):
        self._initial = str(self)
        val = r.get(self.key)
        if val is None:
            return ''
        return val

    def save(self, timeout=-1):
        if self._initial != str(self):
            r.set(self.key, self)
            if timeout == -1:
                r.persist(self.key)
            else:
                r.expire(self.key, timeout)
            return True
        return False
