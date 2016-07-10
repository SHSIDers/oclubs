#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#


"""oclubs.shsid.org Activities."""

from __future__ import absolute_import, unicode_literals

from oclubs.objs.base import BaseObject


class Activity(BaseObject):
    def __init__(self, aid):
        super(Activity, self).__init__(aid)

    # TODO: @property

    @property
    def _data(self):
        return super(Activity, self)._data(
                'activity',
                [('=', 'act_id', self.id)],
                {
                # TODO
                }
            )
