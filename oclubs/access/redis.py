#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

from redis import Redis
from flask import g
import json


r = Redis(host='localhost', port=6379, db=0)


def done():
    for stuff in g.redisStuffList.values():
        stuff.save()


class RedisStuff(object):
    def __init__(self):
        exist = g.get('redisStuffList', None)
        if not exist:
            g.redisStuffList = {}
        g.redisStuffList[self.key] = self
        self._initial = json.dumps(self)
        super(RedisStuff, self).__init__()

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
        changed = self._initial != dumped
        if changed:
            r.set(self.key, dumped)
        if timeout == -1:
            r.persist(self.key)
        else:
            r.expire(self.key, timeout)
        return changed


class RedisDict(dict, RedisStuff):
    def __init__(self, key):
        self.key = key
        dict.__init__(dict(self.load()))
        RedisStuff.__init__(self)


class RedisList(list, RedisStuff):
    def __init__(self, key):
        list.__init__(list(self.load()))
        RedisStuff.__init__(self)


class RedisCache(RedisStuff):
    def __init__(self, key):
        self.key = key
        super(RedisCache, self).__init__(self.load())

    def set(self, value):
        self._value = value

    def get(self):
        return self._value
