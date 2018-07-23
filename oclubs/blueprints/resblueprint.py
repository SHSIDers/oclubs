#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals, division

# for debugging purposes only
from __future__ import print_function
import sys

from datetime import date

from flask import (
    Blueprint, render_template, url_for, request, redirect, flash, abort
)
from flask_login import current_user, login_required, fresh_login_required

from oclubs.enums import UserType, ActivityTime, Building
from oclubs.shared import (
    get_callsign, special_access_required, Pagination, render_email_template,
    download_xlsx, partition, require_student_membership,
    require_past_activity, require_future_activity, require_active_club,
    true_or_fail, form_is_valid, error_or_fail, fail
)
from oclubs.objs import Reservation, Classroom
from oclubs.objs.classroom import classroomSidebarForm, clearSelectionForm

resblueprint = Blueprint('resblueprint', __name__)


@resblueprint.route('viewlist/<resfilter:res_filter>/', defaults={'page': 1},
                    methods=['GET', 'POST'])
@resblueprint.route('viewlist/<resfilter:res_filter>/<int:page>')
def allreservations(res_filter, page):
    '''Display reservations'''
    # generate template parameters
    res_num = 20
    count, res = Reservation.get_reservations_conditions(
        limit=((page-1)*res_num, res_num),
        **res_filter.to_kwargs())
    pagination = Pagination(page, res_num, count)

    # admins get a different page
    if current_user.is_authenticated:
        if current_user.type == UserType.CLASSROOM_ADMIN:
            is_admin = True
    else:
        is_admin = False

    # generate list of possible classrooms to select from based on users
    # selection of other filter options
    available_classrooms = Classroom.get_classroom_conditions(
        building=res_filter.conds[0].value if res_filter.conds[0] else None,
        timeslot=res_filter.conds[1].value if res_filter.conds[1] else None)
    classrooms_list = [(r.room_id, r.room_number)
                       for r in available_classrooms]

    form = classroomSidebarForm()
    # dynamically set the selection form choices
    form.classrooms_list.choices = classrooms_list

    clearBtn = clearSelectionForm()

    if request.method == 'POST':
        # rebuild the res_filter
        temp = list(res_filter.conds)

        # after submit selection
        if form.submit.data:
            if form.classrooms_list.data:
                # convert a list of room_id from form data
                # to a list of room_numbers for res_filter
                temp[2] = [dict(classrooms_list)[id]
                           for id in form.classrooms_list.data]
            else:
                temp[2] = None

        # after clear selection
        if clearBtn.clear.data:
            temp[2] = None

        res_filter.conds = tuple(temp)

        # refresh the page with the update res_filter
        return redirect(url_for('.allreservations', res_filter=res_filter))

    # preserve form selections from the previous session
    defaultSelection = []
    if res_filter.conds[2] is not None:
        # convert a list of room_numbers from res_filter
        # to a list of room_id
        for r in available_classrooms:
            if str(r.room_number) in res_filter.conds[2]:
                defaultSelection.append(r.room_id)
    form.classrooms_list.process_data(defaultSelection)

    return render_template('reservation/allres.html.j2',
                           res=res,
                           pagination=pagination,
                           res_filter=res_filter,
                           form=form,
                           clearBtn=clearBtn,
                           is_admin=is_admin)


@resblueprint.route('/')
def home_redirect():
    return redirect(url_for('.allreservations', res_filter='all'))
