#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

from redis import Redis
from flask import g
import json


r = Redis(host='localhost', port=6379, db=0)


def jsondumps(val):
    


def done(commit=True):
    if commit:
        for stuff in g.redisObjDict.values():
            stuff.save()
    g.redisObjDict.clear()


class RedisStuff(object):
    def __new__(cls, key, timeout):
        exist = g.get('redisObjDict', None)
        if exist:
            if key in g.redisObjDict:
                return g.redisObjDict[key]
        else:
            g.redisObjDict = {}
        obj = super(RedisStuff, cls).__new__(cls)
        obj._fresh = True
        obj.key = key
        obj.timeout = timeout
        return obj

    def __init__(self, loaded):
        if self._fresh:
            g.redisObjDict[self.key] = self
            super(RedisStuff, self).__init__(loaded)
            self._fresh = False
            if isinstance(val, RedisCache):
                self._initial = json.dumps(val.get())
            else:
                self._initial = json.dumps(val)

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

    def save(self):
        dumped = jsondumps(self)
        if self._initial != dumped:
            r.set(self.key, dumped)
        if self.timeout < 0:
            r.persist(self.key)
        else:
            r.expire(self.key, self.timeout)


class RedisDict(RedisStuff, dict):
    def __init__(self, key, timeout):
        super(RedisDict, self).__init__(dict(self.load()))


class RedisList(RedisStuff, list):
    def __init__(self, key, timeout):
        super(RedisList, self).__init__(list(self.load()))


class Cache(object):
    def __init__(self, value):
        self._value = value

    def set(self, value):
        self._value = value

    def get(self):
        return self._value


class RedisCache(RedisStuff, Cache):
    def __init__(self, key, timeout):
        super(RedisCache, self).__init__(self.load())
