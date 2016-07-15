#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#


"""oclubs.shsid.org Base Object."""

from __future__ import absolute_import

import types

from oclubs.access import database


class BaseObject(object):
    _propsdb = None  # subclasses use {}

    def __init__(self, oid):
        super(BaseObject, self).__init__()
        self.__id = oid
        self._dbdata = None
        self._cache = {}

    @property
    def id(self):
        return self.__id

    @property
    def _data(self):
        if self._dbdata is None:
            self._dbdata = database.fetch_onerow(
                self.table,
                self._propsdb,
                [('=', self.identifier, self.id)]
            )

        return self._dbdata

    @classmethod
    def _prop(cls, name, dbname, ie=None):
        if not hasattr(cls, name):
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
                if name and self._dbdata is not None:
                    self._dbdata[name] = value

                database.update_row(
                    self.table,
                    {dbname: value},
                    [('=', self.identifier, self.id)]
                )

            def deleter(self):
                if name in self._cache:
                    del self._cache[name]

                self._dbdata = None

            getter.__name__ = setter.__name__ = deleter.__name__ = name
            setattr(cls, name, property(getter, setter, deleter))

    @classmethod
    def _listprop(cls, name, table, this, that, ie=None):
        if not hasattr(cls, name):
            imp, exp = _get_ie(ie)

            def getter(self):
                if name not in self._cache:
                    tempdata = database.fetch_onecol(
                        table,
                        that,
                        [('=', this, self.id)]
                    )
                    self._cache[name] = [imp(member) for member in tempdata]

                return self._cache[name]

            def deleter(self):
                if name in self._cache:
                    del self._cache[name]

            getter.__name__ = deleter.__name__ = name
            setattr(cls, name, property(getter, None, deleter))

    @classmethod
    def _static_initialize_once(cls):
        if hasattr(cls, '_static_initialized'):
            return True
        cls._static_initialized = True
        return False

    def __eq__(self, other):
        if not isinstance(other, BaseObject):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


def _get_ie(ie):
    if ie is None:
        imp = exp = lambda val: val
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
