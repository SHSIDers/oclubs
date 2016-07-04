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
        self._id = oid

    @property
    def id(self):
        return self._id

    def _data(self, *args, **kwargs):
        if self.__data is None:
            self.__data = database.fetch_onerow(*args, **kwargs)

        return self.__data
