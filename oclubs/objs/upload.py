#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

import os
import subprocess

from PIL import Image

from oclubs.exceptions import UploadNotSupported
from oclubs.objs.base import BaseObject, Property


class Upload(BaseObject):
    table = 'upload'
    identifier = 'upload_id'
    club = Property('upload_club', 'Club')
    uploader = Property('upload_user', 'User')
    location = Property('upload_loc')
    mime = Property('upload_mime')

    # Don't use mimetypes.guess_extension(mime) -- 'image/jpeg' => '.jpe'
    _mimedict = {
        'image/jpeg': '.jpg',
        'image/png': '.png',
    }

    @property
    def location_local(self):
        return self.mk_internal_path(self.location)

    @property
    def location_external(self):
        return self.mk_external_path(self.location)

    @classmethod
    def handle_upload(cls, user, club, file):
        filename = os.urandom(8).encode('hex')
        temppath = os.path.join('/tmp', filename)
        file.save(temppath)

        try:
            # Don't use mimetypes.guess_type(temppath) -- Faked extensions
            mime = subprocess.check_output(
                ['/usr/bin/file', '-bi', temppath]).strip()
            if mime not in cls._mimedict:
                raise UploadNotSupported

            filename = filename + cls._mimedict[mime]
            permpath = cls.mk_internal_path(filename)
            permdir = os.path.dirname(permpath)
            if not os.path.isdir(permdir):
                os.makedirs(permdir, 0o755)

            # resize to 600, 450
            im = Image.open(temppath)
            im.thumbnail((600, 450))
            im.save(permpath)
        finally:
            os.remove(temppath)

        obj = cls.new()
        obj.club = club
        obj.uploader = user
        obj.location = filename
        return obj.create()

    @staticmethod
    def mk_relative_path(filename):
        return os.path.join('images', filename[0], filename[:2], filename)

    @staticmethod
    def mk_internal_path(filename):
        return os.path.join('/srv/oclubs', Upload.mk_relative_path(filename))

    @staticmethod
    def mk_external_path(filename):
        return os.path.join('/', Upload.mk_relative_path(filename))
