#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

from redis import Redis
from flask import g
import json


r = Redis(host='localhost', port=6379, db=0)


def done():
    for stuff in g.redisObjDict.values():
        stuff.save()


class RedisStuff(object):
    def __new__(cls, key):
        exist = g.get('redisObjDict', None)
        if exist:
            if key in g.redisObjDict:
                return g.redisObjDict[key]
        else:
            g.redisObjDict = {}
        obj = super(RedisStuff, cls).__new__(cls)
        obj._fresh = True
        obj.key = key
        return obj

    def __init__(self, loaded):
        if self._fresh:
            g.redisObjDict[self.key] = self
            super(RedisStuff, self).__init__(loaded)
            self._fresh = False
            self._initial = json.dumps(self)

    def load(self):
        val = r.get(self.key)
        if val is None:
            return ''
        try:
            ret = json.loads(val)
        except ValueError:
            r.delete(self.key)
            return ''
        return ret

    def save(self, timeout=-1):
        dumped = json.dumps(self)
        if self._initial != dumped:
            r.set(self.key, dumped)
        if timeout == -1:
            r.persist(self.key)
        else:
            r.expire(self.key, timeout)


class RedisDict(RedisStuff, dict):
    def __init__(self, key):
        super(RedisDict, self).__init__(dict(self.load()))


class RedisList(RedisStuff, list):
    def __init__(self, key):
        super(RedisDict, self).__init__(list(self.load()))


class Cache(object):
    def __init__(self, value):
        self._value = value

    def set(self, value):
        self._value = value

    def get(self):
        return self._value


class RedisCache(RedisStuff, Cache):
    def __init__(self, key):
        super(RedisCache, self).__init__(self.load())
