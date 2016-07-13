#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#


"""oclubs.shsid.org Base Object."""

from __future__ import absolute_import

import os

from oclubs.access import database


class BaseObject(object):
    _propsdb = None  # subclasses use {}
    _props = None  # subclasses use {}

    def __init__(self, oid):
        super(BaseObject, self).__init__()
        self.__id = oid
        self.__data = None
        self._cache = {}

    @property
    def id(self):
        return self.__id

    @property
    def _data(self):
        if self.__data is None:
            self.__data = database.fetch_onerow(
                self.table,
                [('=', self.identifier, self.id)],
                self._propsdb
            )

        return self.__data

    @classmethod
    def _prop(cls, name, dbname, ie=None):
        if name not in cls._props:
            cls._propsdb[dbname] = name

            imp, exp = _get_ie(ie)

            def getter(self):
                if name not in self._cache:
                    self._cache[name] = imp(self._data[name])
                return self._cache[name]

            def setter(self, value):
                if name:
                    self._cache[name] = value

                value = exp(value)
                if name and self.__data is not None:
                    self.__data[name] = value

                database.update_row(
                    self.table,
                    [('=', self.identifier, self.id)],
                    {dbname: value}
                )

            cls._props[name] = property(getter, setter)
        return cls._props[name]

    @classmethod
    def _listprop(cls, name, table, this, that, ie=None):
        if name not in cls._props:
            imp, exp = _get_ie(ie)

            def getter(self):
                if name not in self._cache:
                    tempdata = database.fetch_onecol(
                        table,
                        [('=', this, self.id)],
                        that
                    )
                    self._cache[name] = [imp(member) for member in tempdata]

                return self._cache[name]

            cls._props[name] = property(getter)
        return cls._props[name]

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    # HACK: for preperties
    def __getattr__(self, name):
        if name not in self._props:
            raise AttributeError

        return self._props[name].fget(self)

    def __setattr__(self, name, value):
        if name not in self._props:
            return super(BaseObject, self).__setattr__(name, value)

        return self._props[name].fset(self, value)

    def __delattr__(self, name):
        if name not in self._props:
            return super(BaseObject, self).__delattr__(name)

        return self._props[name].fdel(self)


def _get_ie(ie):
    if ie is None:
        imp = exp = lambda val: val
    elif isinstance(ie, BaseObject):
        imp, exp = ie, lambda val: val.id
    elif isinstance(ie, type(os)):
        imp, exp = ie, ie.dumps
    elif callable(ie):
        imp = exp = ie
    elif isinstance(ie, tuple) and len(ie) == 2 and \
            callable(ie[0]) and callable(ie[1]):
        imp, exp = ie

    return imp, exp
