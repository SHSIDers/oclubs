#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#


"""oclubs.shsid.org Base Object."""

from __future__ import absolute_import

import types
from enum import Enum

from oclubs.access import database


class Property(object):
    """Descriptor class."""
    def __init__(self, dbname, ie=None):
        super(Property, self).__init__()
        self.dbname = dbname
        self.imp, self.exp = _get_ie(ie)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if self.name not in instance._cache:
            instance._cache[self.name] = self.imp(instance._data[self.name])
        return instance._cache[self.name]

    def __set__(self, instance, value):
        instance._cache[self.name] = value

        value = self.exp(value)
        if instance.is_real:
            if instance._dbdata is not None:
                instance._dbdata[self.name] = value

            database.update_row(
                instance.table,
                {self.dbname: value},
                {instance.identifier: instance.id}
            )
        else:
            instance._dbdata = instance._dbdata or {}
            instance._dbdata[self.name] = value

    def __delete__(self, instance):
        if self.name in instance._cache:
            del instance._cache[self.name]

        if instance.is_real:
            instance._dbdata = None
        else:
            if self.name in instance._dbdata:
                del instance._dbdata[self.name]


class ListProperty(object):
    """Descriptor class."""
    def __init__(self, table, this, that, ie=None):
        super(ListProperty, self).__init__()
        self.table = table
        self.this = this
        self.that = that
        self.imp, self.exp = _get_ie(ie)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if self.name not in instance._cache:
            tempdata = database.fetch_onecol(
                self.table,
                self.that,
                {self.this: instance.id}
            )
            instance._cache[self.name] = \
                [self.imp(member) for member in tempdata]

        return instance._cache[self.name]

    def __set__(self, instance, value):
        raise AttributeError("ListProperty is not writable.")

    def __delete__(self, instance):
        if self.name in instance._cache:
            del instance._cache[self.name]


class _BaseMetaclass(type):
    def __new__(meta, name, bases, dct):
        _propsdb = {}
        for key, value in dct.items():
            if isinstance(value, Property):
                _propsdb[value.dbname] = key

                value.name = key
            if isinstance(value, ListProperty):
                value.name = key

        @property
        def _data(self):
            if self._dbdata is None:
                self._dbdata = database.fetch_onerow(
                    self.table,
                    _propsdb,
                    {self.identifier: self.id}
                )

            return self._dbdata

        dct['_data'] = _data

        def create(self):
            if self.is_real:
                raise NotImplementedError
            data = {}
            for key, value in _propsdb.items():
                data[key] = self._dbdata[value]
            self._id = database.insert_row(self.table, data)

            # Reload with newest data from database
            self._dbdata = None
            self._data

        dct['create'] = create

        return super(_BaseMetaclass, meta).__new__(meta, name, bases, dct)

    def __call__(cls, oid):
        self = type.__call__(cls)
        self._id = oid
        self._dbdata = None
        self._cache = {}
        return self


class BaseObject(object):
    __metaclass__ = _BaseMetaclass

    @property
    def id(self):
        if not self.is_real:
            raise NotImplementedError
        return self._id

    @property
    def is_real(self):
        return self._id >= 0

    @classmethod
    def new(cls):
        return cls(-1)

    def __eq__(self, other):
        if not isinstance(other, BaseObject) or not self.is_real:
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


def object_proxy(name):
    return lambda oid: getattr(__import__('oclubs').objs, name)(oid)


def _get_ie(ie):
    if isinstance(ie, tuple) and len(ie) == 2:
        imp, exp = __get_ie(ie[0])[0], __get_ie(ie[1])[1]
    else:
        imp, exp = __get_ie(ie)

    return imp, exp


def __get_ie(ie):
    if ie is None:
        imp = exp = lambda val: val
    elif ie is NotImplemented:
        imp = exp = lambda val: NotImplemented
    elif isinstance(ie, basestring):
        imp, exp = object_proxy(ie), lambda val: val.id
    elif isinstance(ie, types.ModuleType):
        imp, exp = ie.loads, ie.dumps
    elif isinstance(ie, type) and issubclass(ie, BaseObject):
        imp, exp = ie, lambda val: val.id
    elif isinstance(ie, type) and issubclass(ie, Enum):
        imp, exp = ie, lambda val: val.value
    elif callable(ie):
        imp = exp = ie

    return imp, exp
