#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals, division

# for debugging purposes
from __future__ import print_function
import sys

from oclubs.utils.dates import today, tommorow, next_week, \
    DATE_RANGE_MAX

from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, RadioField, TextAreaField
from wtforms.fields.html5 import DateField
from wtforms.validators import InputRequired

from oclubs.enums import Building, ActivityTime, SBAppStatus
from oclubs.objs.classroom import Classroom


class NewReservationForm_Club(FlaskForm):
    building = RadioField(
        'Building',
        choices=[(b.format_name, b.format_name) for b in Building],
        default=Building.XMT.format_name)

    timeslot = RadioField(
        'Timeslot',
        choices=[('noon',
                  ActivityTime.NOON.format_name),
                 (ActivityTime.AFTERSCHOOL.format_name,
                  ActivityTime.AFTERSCHOOL.format_name)],
        default='noon')

    date_selection = DateField(
        'Date',
        default=next_week()[0],
        validators=[InputRequired()])  # next monday

    get_free_classrooms = SubmitField('Check for available classrooms')

    free_classrooms = SelectField(
        'Available classrooms',
        choices=[('unknown', '---')],
        default='unknown')

    SBNeeded = RadioField(
        'Need smartboard?',
        choices=[('yes', 'Yes'),
                 ('no', 'No')],
        default='no')

    SBAppDesc = TextAreaField('Smartboard Application Description',)

    submit = SubmitField('Submit Reservation')

    def check(self):
        building = Building[self.building.data.upper()]
        timeslot = ActivityTime[self.timeslot.data.upper()]
        single_date = self.date_selection.data
        classroom = self.free_classrooms.data
        SBNeeded = self.SBNeeded.data
        SBAppDesc = self.SBAppDesc.data

        if single_date is None:
            self.errors[self.date_selection] = \
                'Please select a date. '
            return False

        if single_date < today():
            self.errors[self.date_selection] = \
                'Sorry, your browser doesn\'t support time travel. ' + \
                'Reservations must be in the future. -.-'
            return False

        if single_date > DATE_RANGE_MAX:
            self.errors[self.date_selection] = \
                'Date should be no later than ' + str(DATE_RANGE_MAX) + \
                '.'
            return False

        # non SB reservations must be at least 1 day in advance
        if SBNeeded == 'no' and single_date < tommorow():
            self.errors[self.date_selection] = \
                'Non-smartboard reservations can be ' + \
                'no earlier than tomorrow.'
            return False

        # SB reservations can only be made for next week
        if SBNeeded == 'yes' and single_date < next_week()[0]:
            self.errors[self.date_selection] = \
                'Smartboard reservations can be ' + \
                'no earlier than next Monday.'
            return False

        timeslot_str = 'Lunch' if timeslot == 'noon' else timeslot.format_name

        if classroom == self.free_classrooms.default:
            self.errors[self.free_classrooms] = \
                'Sorry, no classrooms are available for ' + \
                str(single_date) + ' ' + \
                timeslot_str + \
                ' . Please select another time. '
            return False

        if classroom == 'none':
            self.errors[self.free_classrooms] = \
                'Please select a different time.'

        rdict = Classroom.get_free_classroom_conditions(
            buildings=building,
            timeslot=timeslot,
            dates=single_date)

        realtime_free_rooms = rdict[building][timeslot][single_date]

        if realtime_free_rooms is None:
            self.errors[self.free_classrooms] = \
                'Sorry, no classrooms are available for ' + \
                str(single_date) + ' ' + \
                timeslot_str + \
                ' . Please select another time. '
            return False

        realtime_free_rooms = [r.room_number for r in realtime_free_rooms]

        if classroom not in realtime_free_rooms:
            self.errors[self.free_classrooms] = \
                'Sorry, ' + \
                building + ' ' + \
                classroom + ' ' + \
                'is no longer available for ' + \
                str(single_date) + ' ' + \
                timeslot_str
            return False

        if SBNeeded == 'yes' and len(SBAppDesc) == 0:
            self.errors[self.SBAppDesc] = 'The description is required.'
            return False

        if len(SBAppDesc) > 500:
            self.errors[self.SBAppDesc] = 'The description cannot exceed '
            '500 characters'

        return True


class PairReservation(FlaskForm):
    reservations_for_pairing = SelectField(
        'Unpaired reservations',
        choices=[('none', '-------- None available --------')])

    submit = SubmitField('Pair Reservation')

    def check(self):
        if self.reservations_for_pairing.data == 'none':
            self.errors[self.reservations_for_pairing] = \
                'There are no reservations available for pairing.'
            return False

        return True


class ChangeSBStatusForm(FlaskForm):
    status_choices = [
        (SBAppStatus.PENDING.name.lower(), SBAppStatus.PENDING.format_name),
        (SBAppStatus.APPROVED.name.lower(), SBAppStatus.APPROVED.format_name),
        (SBAppStatus.REJECTED.name.lower(), SBAppStatus.REJECTED.format_name)]
    changeStatus = RadioField(
        'Change status',
        choices=status_choices)
    submit = SubmitField('Change')


# different forms with same field names will mix the data
# ? because request disregards form id and only field id ?
class ChangeDirectorsApprovalForm(FlaskForm):
    changeDApproval = RadioField(
        'Change Director\'s Approval',
        choices=[('True', 'Approved'),
                 ('False', 'Not approved')])
    submit = SubmitField('Change')


class ChangeInstructorsApprovalForm(FlaskForm):
    changeIApproval = RadioField(
        'Change Instructor\'s Approval',
        choices=[('True', 'Approved'),
                 ('False', 'Not approved')])
    submit = SubmitField('Change')


class ChangeCanReservationForm(FlaskForm):
    changeCanReserve = RadioField(
        'Change Reservation Privileges',
        choices=[('True', 'Allowed to Reserve'),
                 ('False', 'Not allowed to Reserve')])
    submit = SubmitField('Change')


class ChangeCanSmartboardForm(FlaskForm):
    changeCanSB = RadioField(
        'Change Smartboard Privileges',
        choices=[('True', 'Allowed to apply for smartboard'),
                 ('False', 'Not allowed to apply for smartboard')])
    submit = SubmitField('Change')
