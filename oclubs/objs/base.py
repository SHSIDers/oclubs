#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#


"""oclubs.shsid.org Base Object."""

from __future__ import absolute_import

import types
from enum import Enum

from oclubs.access import database, elasticsearch


class Property(object):
    """Descriptor class."""
    def __init__(self, dbname, ie=None, search=False):
        super(Property, self).__init__()
        self.dbname = dbname
        self.imp, self.exp = _get_ie(ie)
        self.search = _get_search(search, ie)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if self.name not in instance._cache:
            instance._cache[self.name] = self.imp(instance._data[self.name])
        return instance._cache[self.name]

    def __set__(self, instance, value):
        # Proxies can't pass isinstance check
        try:
            value = value._get_current_object()
        except AttributeError:
            pass

        instance._cache[self.name] = value

        dbvalue = self.exp(value)
        if instance.is_real:
            if instance._dbdata is None:
                instance._data

            if dbvalue == instance._dbdata[self.name]:
                return

            instance._dbdata[self.name] = dbvalue

            database.update_row(
                instance.table,
                {self.dbname: dbvalue},
                {instance.identifier: instance.id}
            )

            if self.search:
                elasticsearch.update(
                    instance.table,
                    instance.id,
                    {self.name: self.search(value)}
                )
        else:
            instance._dbdata = instance._dbdata or {}
            instance._dbdata[self.name] = dbvalue

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
        _essearches = []

        for key, value in dct.items():
            if isinstance(value, Property):
                _propsdb[value.dbname] = key
                if value.search:
                    _essearches.append(value)

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

            if _essearches:
                _esdata = {}
                for prop in _essearches:
                    _esdata[prop.name] = prop.search(self._cache[prop.name])

                elasticsearch.create(self.table, self.id, _esdata)

            # Reload with newest data from database
            self._dbdata = None
            self._data

            return self

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
        return self._id > 0

    @property
    def callsign(self):
        return str(self.id) + '_' + self.name.replace(' ', '_')

    @classmethod
    def new(cls):
        return cls(0)

    def __eq__(self, other):
        if not isinstance(other, BaseObject):
            return NotImplemented
        try:
            return self.id == other.id
        except NotImplementedError:
            return NotImplemented

    def __ne__(self, other):
        if not isinstance(other, BaseObject):
            return NotImplemented
        try:
            return self.id != other.id
        except NotImplementedError:
            return NotImplemented

    def __hash__(self):
        return hash(self.id)


def object_proxy(name):
    return lambda oid: getattr(__import__('oclubs').objs, name)(oid)


def _get_ie(ie):
    if isinstance(ie, tuple) and len(ie) == 2:
        imp, exp = __get_ie(ie[0])[0], __get_ie(ie[1])[1]
    else:
        imp, exp = __get_ie(ie)

    return (lambda val: None if val is None else imp(val),
            lambda val: None if val is None else exp(val))


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


def _get_search(search, ie):
    search = __get_search(search, ie)
    if search:
        return lambda val: None if val is None else search(val)


def __get_search(search, ie):
    if search is False:
        return None
    if search is True:
        if isinstance(ie, tuple):
            ie = ie[1]
        return __get_search(ie, False)
    elif search is None:
        return lambda val: val
    elif isinstance(search, basestring):
        if search == 'User':
            return lambda val: val.passportname
        elif search == 'FormattedText':
            return lambda val: val.raw
        else:
            return lambda val: val.name
    elif isinstance(search, type) and issubclass(search, Enum):
        return lambda val: val.format_name
    elif callable(search):
        return search

    return None
