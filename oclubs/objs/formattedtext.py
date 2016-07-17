#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#


"""oclubs.shsid.org Formatted Text."""

from __future__ import absolute_import, unicode_literals

from flask import Markup

from oclubs.objs.base import BaseObject, Property


class FormattedText(BaseObject):
    table = 'text'
    identifier = 'text_id'
    _data = Property('text_data')
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
                self._raw = self._data
        return self._raw

    @property
    def formatted(self):
        if self._formatted is None:
            # TODO
            self._formatted = Markup(self.raw)
        return self._formatted
