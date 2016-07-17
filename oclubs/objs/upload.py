#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#


"""oclubs.shsid.org Formatted Text."""

from __future__ import absolute_import

from oclubs.objs.base import BaseObject, Property


class Upload(BaseObject):
    table = 'upload'
    identifier = 'upload_id'
    club = Property('upload_club', 'Club')
    uploader = Property('upload_user', 'User')
    location_local = Property('upload_loc')
    mime = Property('upload_mime')

    @property
    def location_external(self):
        # TODO
        return self.location_local
