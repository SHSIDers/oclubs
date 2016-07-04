#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#


"""oclubs.shsid.org Formatted Text."""

from __future__ import absolute_import

from oclubs.objs import User, Club
from oclubs.objs.base import BaseObject


class FormattedText(BaseObject):
    def __init__(self, uid):
        super(FormattedText, self).__init__(uid)
        self._location_local = self._location_external = None

    @property
    def club(self):
        if self._club is None:
            self._club = Club(self._data['club'])
        return self._club

    @property
    def uploader(self):
        if self._uploader is None:
            self._uploader = User(self._data['uploader'])
        return self._uploader

    @property
    def location_local(self):
        if self._location_local is None:
            # TODO
            self._location_local = self._data['location']
        return self._location_local

    @property
    def location_external(self):
        if self._location_external is None:
            # TODO
            self._location_external = self._data['location']
        return self._location_external

    @property
    def mime(self):
        return self._data['mime']

    @property
    def _data(self):
        return super(FormattedText, self)._data(
                'upload',
                [('=', 'upload_id', self.id)],
                {
                    'upload_club': 'club',
                    'upload_user': 'uploader',
                    'upload_loc': 'location',
                    'upload_mime': 'mine'
                }
            )
