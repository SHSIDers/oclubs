#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals, division

from oclubs.access import database
from oclubs.objs.base import BaseObject, Property, paged_db_read
from oclubs.enums import Building


class Classroom(BaseObject):
    table = 'classroom'
    identifier = 'room_id'
    room_number = Property('room_number')
    studentsToUseLunch = Property('room_studentsToUseLunch', bool)
    studentsToUseAfternoon = Property('room_studentsToUseAfternoon', bool)
    building = Property('room_building', Building)
    desc = Property('room_desc')

    @property
    def location(self):
        ret = self.building.format_name + " " + self.room_number.upper()
        return ret

    @classmethod
    @paged_db_read
    def get_classroom_conditions(cls, additional_conds=None, building=None,
                                 pager=None):
        conds = {}
        if additional_conds:
            conds.update(additional_conds)

        conds['where'] = conds.get('where', [])

        if building is not None:
            conds['where'].append(('=', 'room_building', building))

        pager_fetch, pager_return = pager

        ret = pager_fetch(database.fetch_onecol,
                          cls.table,
                          cls.room_number,
                          conds,
                          distinct=True)

        ret = [cls(item) for item in ret]

        return pager_return(ret)
