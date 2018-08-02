#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals, division

# for debugging purposes
from __future__ import print_function
import sys

from oclubs.utils.dates import today, ONE_DAY, DATE_RANGE_MIN, DATE_RANGE_MAX

from flask_wtf import FlaskForm
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms import SelectMultipleField, SubmitField, RadioField
from wtforms.fields.html5 import DateField


class MultiCheckboxForm(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class ClassroomSidebarForm(FlaskForm):
    classrooms_list = MultiCheckboxForm('Classrooms', coerce=int)
    submit = SubmitField('Submit selection')


class ClearSelectionForm(FlaskForm):
    clear = SubmitField('Clear selection')


class ViewClassroomsForm(FlaskForm):
    viewclassroom_options = RadioField(
        'View classrooms',
        choices=[('all_classrooms', 'All classrooms'),
                 ('free_classrooms', 'Available classrooms')],
        default='all_classrooms'
    )
    date_options = RadioField(
        'Date',
        choices=[('today', 'Today'),
                 ('tmrw', 'Tomorrow'),
                 ('thisweek', 'This week'),
                 ('nextweek', 'Next week'),
                 ('nextnextweek', 'Next next week'),
                 ('singledate', 'Single date'),
                 ('daterange', 'Date range')],
        default='today')
    date_select_start = DateField(default=today())
    date_select_end = DateField(default=today() + ONE_DAY)
    submit = SubmitField('Submit selection')

    def check(self):
        if self.date_options.data == 'singledate':
            if self.date_select_start.data is None:
                self.errors[self.date_select_start] = \
                    "Please enter a date. "
                return False
            if self.date_select_start.data < DATE_RANGE_MIN:
                self.errors[self.date_select_start] = \
                    "Date should be no earlier than " + str(DATE_RANGE_MIN) + \
                    "."
                return False
            if self.date_select_start.data > DATE_RANGE_MAX:
                self.errors[self.date_select_start] = \
                    "Date should be no later than " + str(DATE_RANGE_MAX) + \
                    "."
                return False
        if self.date_options.data == 'daterange':
            if self.date_select_start.data is None and \
                    self.date_select_end.data is None:
                self.errors[self.date_select_start] = \
                    "Please enter start and end dates."
                return False
            if self.date_select_start.data is None:
                self.errors[self.date_select_start] = \
                    "Please enter a start date."
                return False
            if self.date_select_end.data is None:
                self.errors[self.date_select_end] = \
                    "Please enter an end date."
                return False
            if self.date_select_start.data >= self.date_select_end.data:
                self.errors[self.date_select_start] = \
                    "Start date should be earlier than end date."
                return False
            if self.date_select_start.data < DATE_RANGE_MIN or \
                    self.date_select_end.data < DATE_RANGE_MIN:
                self.errors[self.date_select_start] = \
                    "Date range should be no earlier than " + \
                    str(DATE_RANGE_MIN) + "."
                return False
            if self.date_select_start.data > DATE_RANGE_MAX or \
                    self.date_select_end.data > DATE_RANGE_MAX:
                self.errors[self.date_select_end] = \
                    "Date range should be no later than " + \
                    str(DATE_RANGE_MAX) + "."
                return False
        return True
