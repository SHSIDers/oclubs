#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#


"""oclubs.shsid.org Base Object."""

from __future__ import absolute_import

from oclubs.access import database


class BaseObject(object):
    def __init__(self, oid):
        super(BaseObject, self).__init__()
        self.__id = oid

    @property
    def id(self):
        return self.__id

    def _data(self, coldict):
        if self.__data is None:
            self.__data = database.fetch_onerow(
                self.table,
                [('=', self.identifier, self.id)],
                coldict
            )

        return self.__data

    def _setdata(self, dictkey, databasekey, value):
        if dictkey and self.__data is not None:
            self.__data[dictkey] = value

        database.update_row(
            self.table,
            [('=', self.identifier, self.id)],
            {databasekey: value}
        )

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
