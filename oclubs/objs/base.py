#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#


"""oclubs.shsid.org Base Object."""

from __future__ import absolute_import

import types

from oclubs.access import database


class Property(object):
    def __init__(self, dbname, ie=None):
        super(Property, self).__init__()
        self.dbname = dbname
        self.ie = _get_ie(ie)


class ListProperty(object):
    """docstring for ListProperty"""
    def __init__(self, table, this, that, ie=None):
        super(ListProperty, self).__init__()
        self.table = table
        self.this = this
        self.that = that
        self.ie = _get_ie(ie)


class _BaseMetaclass(type):
    def __new__(meta, name, bases, dct):
        _propsdb = {}
        for key, value in dct.items():
            if isinstance(value, Property):
                _propsdb[value.dbname] = key

                dct[key] = meta.create_property(key, value)
            if isinstance(value, ListProperty):
                dct[key] = meta.create_listproperty(key, value)

        @property
        def _data(self):
            if self._dbdata is None:
                self._dbdata = database.fetch_onerow(
                    self.table,
                    self._propsdb,
                    [('=', self.identifier, self.id)]
                )

            return self._dbdata

        dct['_data'] = _data

        @property
        def id(self):
            return self._id
        dct['id'] = id

        return super(_BaseMetaclass, meta).__new__(meta, name, bases, dct)

    @staticmethod
    def create_property(name, value):
        imp, exp = value.ie

        def getter(self):
            if name not in self._cache:
                self._cache[name] = imp(self._data[name])
            return self._cache[name]

        def setter(self, value):
            if name:
                self._cache[name] = value

            value = exp(value)
            if name and self._dbdata is not None:
                self._dbdata[name] = value

            database.update_row(
                self.table,
                {value.dbname: value},
                [('=', self.identifier, self.id)]
            )

        def deleter(self):
            if name in self._cache:
                del self._cache[name]

            self._dbdata = None

        getter.__name__ = setter.__name__ = deleter.__name__ = name
        return property(getter, setter, deleter)

    @staticmethod
    def create_listproperty(name, value):
        imp, exp = value.ie

        def getter(self):
            if name not in self._cache:
                tempdata = database.fetch_onecol(
                    value.table,
                    value.that,
                    [('=', value.this, self.id)]
                )
                self._cache[name] = [imp(member) for member in tempdata]

            return self._cache[name]

        def deleter(self):
            if name in self._cache:
                del self._cache[name]

        getter.__name__ = deleter.__name__ = name
        return property(getter, None, deleter)

    def __call__(cls, oid):
        self = type.__call__(cls)
        self._id = oid
        self._dbdata = None
        self._cache = {}
        return self


class BaseObject(object):
    __metaclass__ = _BaseMetaclass

    def __eq__(self, other):
        if not isinstance(other, BaseObject):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


def object_proxy(name):
    return lambda oid: getattr(__import__('oclubs').objs, name)(oid)


def _get_ie(ie):
    if ie is None:
        imp = exp = lambda val: val
    elif isinstance(ie, basestring):
        imp, exp = object_proxy(ie), lambda val: val.id
    elif isinstance(ie, BaseObject):
        imp, exp = ie, lambda val: val.id
    elif isinstance(ie, types.ModuleType):
        imp, exp = ie, ie.dumps
    elif callable(ie):
        imp = exp = ie
    elif isinstance(ie, tuple) and len(ie) == 2 and \
            callable(ie[0]) and callable(ie[1]):
        imp, exp = ie

    return imp, exp
