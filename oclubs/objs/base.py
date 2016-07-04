#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#


"""oclubs.shsid.org Base Object."""

from __future__ import absolute_import

from oclubs.access import database

from oclubs.objs import User, Club

class BaseObject(object):
    def __init__(self, oid):
        super(BaseObject, self).__init__()
        self.__id = oid

    @property
    def id(self):
        return self.__id

    def _data(self, *args, **kwargs):
        if self.__data is None:
            self.__data = database.fetch_onerow(*args, **kwargs)

        return self.__data

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
