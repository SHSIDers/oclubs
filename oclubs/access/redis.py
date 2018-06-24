#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""
Module to access Redis key-value storage.

Access is in a object fashion, with objects instantiated with the key. The
serialization is done with JSON.
"""

from __future__ import absolute_import, unicode_literals

from abc import ABCMeta

from redis import Redis
from flask import g
import json

from oclubs.access.secrets import get_secret

r = Redis(host='localhost', port=6379, db=0, password=get_secret('redis_pw'))
r_url_celery = 'redis://:' + get_secret('redis_pw') + '@localhost:6379/'


def _done(commit=True):
    if g.get('redisObjDict', None):
        if commit:
            g.redisPipeline = g.get('redisPipeline', r.pipeline())
            for stuff in g.redisObjDict.values():
                stuff.save()

            g.redisPipeline.execute()
            del g.redisPipeline
        g.redisObjDict.clear()
        del g.redisObjDict


class _RedisMetaclass(ABCMeta):
    def __call__(cls, *args, **kwargs):
        cached = g.get('redisObjDict', None)
        self = cls.__new__(cls, *args, **kwargs)

        if cached:
            if self.key in g.redisObjDict:
                return g.redisObjDict[self.key]
        else:
            g.redisObjDict = {}

        self.__init__()

        g.redisObjDict[self.key] = self

        return self


class RedisStuff(object):
    """
    Superclass of all redis stuffs.

    :param basestring key: redis key
    :param int timeout: timeyt in seconds for the key, negative values
        are forever.
    """
    __metaclass__ = _RedisMetaclass

    def __new__(cls, key, timeout):
        self = super(RedisStuff, cls).__new__(cls)
        self.key = key
        self.timeout = timeout
        return self

    def __init__(self):
        try:
            initial = self.load(self.key)
            data = self.unserialize(initial)
            super(RedisStuff, self).__init__(data)
            self.new = False
        except (TypeError, ValueError, KeyError):
            super(RedisStuff, self).__init__()
            self.new = True

        self._initial = self.serialize(self)

    @staticmethod
    def load(key):
        """
        Load a value from Redis.

        :param basestring key: redis key
        :returns: the value associated with the key
        :rtype: basestring
        :raises KeyError: if key is not found
        """
        val = r.get(key)
        if val is None:
            raise KeyError
        return val

    @staticmethod
    def unserialize(data):
        """
        Unserialize data.

        :param basestring data: data to unserialize
        :returns: unserialized data
        """
        return json.loads(data)

    def save(self):
        """Save data to redis."""
        p = g.get('redisPipeline', r)

        if not self:
            p.delete(self.key)
            return

        dumped = self.serialize(self)
        if self._initial != dumped:
            p.set(self.key, dumped)
        if self.timeout < 0:
            p.persist(self.key)
        else:
            p.expire(self.key, self.timeout)

    @staticmethod
    def serialize(obj):
        """
        Serialize object.

        :param obj: object to serialize
        :returns: serialized object
        :rtype: basestring
        """
        return json.dumps(obj)

    @property
    def modified(self):
        """bool indicating if value has been modified."""
        return self.serialize(self) != self._initial

    def detach(self):  # in TARS's voice
        """No longer have access.done() operate on this object."""
        try:
            del g.redisObjDict[self.key]
        except KeyError:
            pass
        return self


class RedisDict(RedisStuff, dict):
    """A dict on Redis."""
    pass


class RedisList(RedisStuff, list):
    """A list on Redis."""
    pass


class ImmutableMixin(object):
    """
    Mixin to work with immutable types on redis.

    :param value: initial value
    """
    def __init__(self, value=''):
        self._value = value

    def set(self, value):
        """Set value."""
        self._value = value

    def get(self):
        """Get value."""
        return self._value

    def __nonzero__(self):
        return bool(self._value)


class RedisCache(RedisStuff, ImmutableMixin):
    """An immutable object on Redis for indirect access."""
    def serialize(self, obj):
        return super(RedisCache, self).serialize(obj.get())
