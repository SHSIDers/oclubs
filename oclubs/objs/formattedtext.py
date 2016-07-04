#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#


"""oclubs.shsid.org Formatted Text."""

from __future__ import absolute_import, unicode_literals

from flask import Markup

from oclubs.objs.base import BaseObject


class FormattedText(BaseObject):
    def __init__(self, tid):
        super(FormattedText, self).__init__(tid)
        self._raw = self._formatted = None

    @property
    def raw(self):
        if self._raw is None:
            flags = self.__data['flags'].split(',')
            if 'external' in flags:
                # TODO
                pass
            else:
                self._raw = self._data['data']
        return self._raw

    @property
    def formatted(self):
        if self._formatted is None:
            # TODO
            self._formatted = Markup(self.raw)
        return self._formatted

    @property
    def _data(self):
        return super(FormattedText, self)._data(
                'text',
                [('=', 'text_id', self.id)],
                {
                    'text_data': 'data',
                    'text_flags': 'flags'
                }
            )
