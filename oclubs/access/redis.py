#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
from __future__ import absolute_import, unicode_literals

from redis import Redis
import json

r = Redis(host='localhost', port=6379, db=0)


class RedisStuff(object):
    def load(self):
        val = r.get(self.key)
        if val is None:
            return None
        try:
            ret = json.loads(val)
        except ValueError:
            r.delete(self.key)
            return None
        return ret

    def save(self, timeout=-1):
        r.set(self.key, json.dumps(self))
        if timeout < 0:
            r.persist(self.key)
        else:
            r.expire(self.key, timeout)


class RedisDict(dict, RedisStuff):
    def __init__(self, key):
        self.key = key
        super(RedisDict, self).__init__(self.load())


class RedisList(list, RedisStuff):
    def __init__(self, key, initial=None):
        self.key = key
        super(RedisList, self).__init__(self.load())
