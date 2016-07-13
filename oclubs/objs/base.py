#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#


"""oclubs.shsid.org Base Object."""

import os

from __future__ import absolute_import

from oclubs.access import database


class BaseObject(object):
    def __init__(self, oid):
        super(BaseObject, self).__init__()
        self.__id = oid
        self.__data = None
        self.__cache = {}

    @property
    def id(self):
        return self.__id

    @property
    def _data(self):
        if self.__data is None:
            self.__data = database.fetch_onerow(
                self.table,
                [('=', self.identifier, self.id)],
                self._dbprops
            )

        return self.__data

    @classmethod
    def _prop(cls, dbname, name, ie=None):
        if name not in cls._props:
            cls._dbprops[dbname] = name

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
    def _listprop(cls, table, this, that, name, ie=None):
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
