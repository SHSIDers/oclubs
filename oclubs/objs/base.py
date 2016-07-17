#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#


"""oclubs.shsid.org Base Object."""

from __future__ import absolute_import

import types

from oclubs.access import database


class Property(property):
    def __init__(prop, dbname, ie=None):
        prop.dbname = dbname
        prop.imp, prop.exp = _get_ie(ie)
        super(Property, prop).__init__(prop.getf, prop.setf, prop.delf)

    def getf(prop, self):
        if prop.name not in self._cache:
            self._cache[prop.name] = prop.imp(self._data[prop.name])
        return self._cache[prop.name]

    def setf(prop, self, value):
        self._cache[prop.name] = value

        value = prop.exp(value)
        if self.is_real:
            if self._dbdata is not None:
                self._dbdata[prop.name] = value

            database.update_row(
                self.table,
                {prop.dbname: value},
                {self.identifier: self.id}
            )
        else:
            self._dbdata = self._dbdata or {}
            self._dbdata[prop.name] = value

    def delf(prop, self):
        if prop.name in self._cache:
            del self._cache[prop.name]

        if self.is_real:
            self._dbdata = None
        else:
            if prop.name in self._dbdata:
                del self._dbdata[prop.name]


class ListProperty(property):
    """docstring for ListProperty"""
    def __init__(prop, table, this, that, ie=None):
        prop.table = table
        prop.this = this
        prop.that = that
        prop.imp, prop.exp = _get_ie(ie)
        super(ListProperty, prop).__init__(prop.getf, None, prop.delf)

    def getf(prop, self):
        if prop.name not in self._cache:
            tempdata = database.fetch_onecol(
                prop.table,
                prop.that,
                {prop.this: self.id}
            )
            self._cache[prop.name] = [prop.imp(member) for member in tempdata]

        return self._cache[prop.name]

    def delf(prop, self):
        if prop.name in self._cache:
            del self._cache[prop.name]


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
            del self._dbdata
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
    elif isinstance(ie, BaseObject):
        imp, exp = ie, lambda val: val.id
    elif isinstance(ie, types.ModuleType):
        imp, exp = ie.loads, ie.dumps
    elif callable(ie):
        imp = exp = ie

    return imp, exp
