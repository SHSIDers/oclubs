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
    def __new__(cls, *args, **kwargs):
        exist = g.get('redisObjDict', None)
        if exist and args[0] in g.redisObjDict:
                return g.redisObjDict[args[0]]
        obj = object.__new__(cls, *args, **kwargs)
        obj._fresh = True
        return obj

    def __init__(self, loaded):
        if self._fresh:
            exist = g.get('redisObjDict', None)
            if not exist:
                g.redisObjDict = {self.key: self}
            else:
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
        self.key = key
        super(RedisDict, self).__init__(dict(self.load()))


class RedisList(RedisStuff, list):
    def __init__(self, key):
        self.key = key
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
        self.key = key
        super(RedisCache, self).__init__(self.load())
