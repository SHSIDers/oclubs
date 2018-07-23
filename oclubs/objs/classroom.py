#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals, division

from flask_wtf import FlaskForm
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms import SelectMultipleField, SubmitField, SelectField

from oclubs.access import database
from oclubs.objs.base import BaseObject, Property, paged_db_read
from oclubs.enums import Building, ActivityTime


class Classroom(BaseObject):
    table = 'classroom'
    identifier = 'room_id'
    room_id = Property('room_id')
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
                                 timeslot=None, order_by_room_number=True,
                                 pager=None):
        conds = {}
        if additional_conds:
            conds.update(additional_conds)

        conds['where'] = conds.get('where', [])

        if building:
            conds['where'].append(('=', 'room_building', building))

        if timeslot:
            if timeslot == ActivityTime.AFTERSCHOOL.value:
                conds['where'].append(('=',
                                      'room_studentsToUseAfternoon', '1'))
            if timeslot == ActivityTime.NOON.value:
                conds['where'].append(('=', 'room_studentsToUseLunch', '1'))

        if order_by_room_number:
            conds['order'] = conds.get('order', [])
            conds['order'].append(('room_number', True))

        pager_fetch, pager_return = pager

        ret = pager_fetch(database.fetch_onecol,
                          cls.table,
                          cls.identifier,
                          conds)

        ret = [cls(item) for item in ret]

        return pager_return(ret)


class MultiCheckboxForm(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class classroomSidebarForm(FlaskForm):
    classrooms_list = MultiCheckboxForm('Classrooms', coerce=int)
    submit = SubmitField('Submit selection')


class clearSelectionForm(FlaskForm):
    clear = SubmitField('Clear selection')
