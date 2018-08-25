#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals, division

from oclubs.utils.dates import today, ONE_DAY, DATE_RANGE_MIN, DATE_RANGE_MAX

from flask_wtf import FlaskForm
from wtforms import SelectField, SelectMultipleField, SubmitField, RadioField
from wtforms.fields.html5 import DateField
from wtforms.validators import InputRequired


class Select2MultipleField(SelectMultipleField):

    def pre_validate(self, form):
        # Prevent "not a valid choice" error
        pass

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = ",".join(valuelist)
        else:
            self.data = ""


class ClassroomSidebarForm(FlaskForm):
    classrooms_list = Select2MultipleField('Classrooms', coerce=int)
    submit_classrooms = SubmitField('Submit')


class ClearSelectionForm(FlaskForm):
    clear = SubmitField('Clear')


class ViewClassroomsForm(FlaskForm):
    # all_classrooms choice is no longer not used,
    # relevant code has been commented out
    viewclassroom_options = RadioField(
        'View classrooms',
        choices=[('all_classrooms', 'All classrooms'),
                 ('free_classrooms', 'Available classrooms')],
        default='free_classrooms'
    )
    date_options = SelectField(
        'Date',
        choices=[('today', 'Today'),
                 ('tmrw', 'Tomorrow'),
                 ('thisweek', 'This week'),
                 ('nextweek', 'Next week'),
                 ('nextnextweek', 'Next next week'),
                 ('singledate', 'Single date'),
                 ('daterange', 'Date range')],
        default='today')
    date_select_start = DateField(
        default=today(),
        validators=[InputRequired()])
    date_select_end = DateField(
        default=today() + ONE_DAY,
        validators=[InputRequired()])
    submit = SubmitField('Submit')

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
