#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

import bleach
from flask import Markup
from markdown import markdown

from oclubs.objs.base import BaseObject, Property


ALLOWED_TAGS = bleach.ALLOWED_TAGS
# We exclude <img>
ALLOWED_TAGS += ['p', 'br', 'hr', 'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']


class FormattedText(BaseObject):
    table = 'text'
    identifier = 'text_id'
    _blob = Property('text_data')
    _flags = Property('text_flags',
                      (lambda x: x.split(','), lambda x: ','.join(x)))

    def __init__(self):
        super(FormattedText, self).__init__()
        self._raw = self._formatted = None

    @property
    def raw(self):
        if self._raw is None:
            if 'external' in self._flags:
                # TODO
                pass
            else:
                self._raw = self._blob.decode('utf-8')
        return self._raw

    @property
    def formatted(self):
        if self._formatted is None:
            self._formatted = Markup(self.format(self.raw))
        return self._formatted

    @staticmethod
    def format(rawstr):
        return bleach.clean(
            markdown(
                rawstr,
                output_format='html5',
                lazy_ol=False
            ),
            tags=ALLOWED_TAGS
        )
