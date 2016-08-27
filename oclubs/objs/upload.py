#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

import os

from PIL import Image
import magic

from oclubs.access import fs
from oclubs.exceptions import UploadNotSupported
from oclubs.objs.base import BaseObject, Property


class Upload(BaseObject):
    table = 'upload'
    identifier = 'upload_id'
    club = Property('upload_club', 'Club')
    uploader = Property('upload_user', 'User')
    _location = Property('upload_loc')
    mime = Property('upload_mime')

    # Don't use mimetypes.guess_extension(mime) -- 'image/jpeg' => '.jpe'
    _mimedict = {
        'image/jpeg': '.jpg',
        'image/png': '.png',
    }

    @property
    def id(self):
        return self._id

    @property
    def location_local(self):
        if self.is_real:
            return self.mk_internal_path(self._location)
        else:
            return self.mk_internal_path(-self.id, False)

    @property
    def location_external(self):
        if self.is_real:
            return self.mk_external_path(self._location)
        else:
            return self.mk_external_path(-self.id, False)

    @classmethod
    def handle(cls, user, club, file):
        filename = os.urandom(8).encode('hex')
        temppath = os.path.join('/tmp', filename)
        file.save(temppath)

        try:
            # Don't use mimetypes.guess_type(temppath) -- Faked extensions
            mime = magic.from_file(temppath, mime=True)
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
            im.save(permpath, optimize=True)
            fs.watch(permpath)
        finally:
            os.remove(temppath)

        obj = cls.new()
        obj.club = club
        obj.uploader = user
        obj._location = filename
        obj.mime = mime
        return obj.create()

    @staticmethod
    def mk_relative_path(filename, is_upload=True):
        if is_upload:
            return os.path.join('images', filename[0], filename[:2], filename)
        else:
            return os.path.join('static/images/icons', 'icon%d.jpg' % filename)

    @staticmethod
    def mk_internal_path(filename, is_upload=True):
        return os.path.join('/srv/oclubs',
                            Upload.mk_relative_path(filename, is_upload))

    @staticmethod
    def mk_external_path(filename, is_upload=True):
        return os.path.join('/', Upload.mk_relative_path(filename, is_upload))
