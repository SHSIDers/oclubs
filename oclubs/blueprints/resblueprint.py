#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals, division

from __future__ import print_function
import sys

from datetime import date

from flask import (
    Blueprint, render_template, url_for, request, redirect, abort,
    jsonify, flash
)
from flask_login import current_user

from oclubs.utils.dates import today, str_to_date_dict, date_to_str_dict, \
    int_to_dateobj
from oclubs.enums import UserType, ActivityTime, Building, \
    SBAppStatus, ResStatus
from oclubs.shared import (
    get_callsign_decorator, special_access_required, Pagination
)
from oclubs.objs import Club, Reservation, Classroom
from oclubs.forms.classroom_forms import (
    ClassroomSidebarForm, ClearSelectionForm, ViewClassroomsForm
)
from oclubs.forms.reservation_forms import (
    NewReservationForm,
    ChangeSBStatusForm, ChangeDirectorsApprovalForm,
    ChangeInstructorsApprovalForm,
    ChangeCanReservationForm, ChangeCanSmartboardForm
)
from oclubs.exceptions import NoRow

resblueprint = Blueprint('resblueprint', __name__)


@resblueprint.route('/viewres/<resfilter:res_filter>/', defaults={'page': 1},
                    methods=['GET', 'POST'])
@resblueprint.route('/viewres/<resfilter:res_filter>/<int:page>',
                    methods=['GET', 'POST'])
def viewreservations(res_filter, page):
    '''Display reservations'''
    # generate template parameters
    res_num = 20
    count, res = Reservation.get_reservations_conditions(
        limit=((page-1)*res_num, res_num),
        **res_filter.to_kwargs())
    pagination = Pagination(page, res_num, count)

    print(res, file=sys.stderr)

    # admins get a different page
    is_admin = False
    if current_user.is_authenticated:
        if current_user.type == UserType.CLASSROOM_ADMIN or \
                current_user.type == UserType.DIRECTOR:
            is_admin = True

    # generate list of possible classrooms to select from based on users
    # selection of other filter options
    available_classrooms = Classroom.get_classroom_conditions(
        buildings=res_filter.conds[0] if res_filter.conds[0] else None,
        timeslot=res_filter.conds[1] if res_filter.conds[1] else None)
    classrooms_list = [(str(r.id), r.room_number)
                       for r in available_classrooms]

    form = ClassroomSidebarForm()
    # dynamically set the selection form choices
    form.classrooms_list.choices = classrooms_list

    clearBtn = ClearSelectionForm()

    if request.method == 'POST':
        # rebuild the res_filter
        temp_filter = list(res_filter.conds)

        # after submit selection
        if form.submit_classrooms.data:
            if form.classrooms_list.data:
                selected_classrooms_id = \
                    str(form.classrooms_list.data).split(',')
                # convert a list of room_id from form data
                # to a list of room_numbers for res_filter
                temp_filter[2] = [dict(classrooms_list)[id]
                                  for id in selected_classrooms_id]
            else:
                temp_filter[2] = None

        # after clear selection
        if clearBtn.clear.data:
            temp_filter[2] = None

        res_filter.conds = tuple(temp_filter)

        # refresh the page with the updated res_filter
        return redirect(url_for('.viewreservations', res_filter=res_filter))

    # preserve form selections from the previous session
    defaultSelection = []
    if res_filter.conds[2] is not None:
        # convert a list of room_numbers from res_filter
        # to a list of room_id
        for r in available_classrooms:
            if str(r.room_number) in res_filter.conds[2]:
                defaultSelection.append(r.id)
    form.classrooms_list.process_data(defaultSelection)

    return render_template('reservation/viewres.html.j2',
                           is_viewres=True,
                           res=res,
                           pagination=pagination,
                           res_filter=res_filter,
                           form=form,
                           clearBtn=clearBtn,
                           is_admin=is_admin)


@resblueprint.route('/')
def res_home_redirect():
    return redirect(url_for('.viewclassrooms', room_filter='all'))


@resblueprint.route('/viewres')
@resblueprint.route('/viewres/')
def viewres_redirect():
    return redirect(url_for('.viewreservations', res_filter='all'))


@resblueprint.route('/viewroom')
@resblueprint.route('/viewroom/')
def viewroom_redirect():
    return redirect(url_for('.viewclassrooms', room_filter='all'))


@resblueprint.route('/viewroom/<roomfilter:room_filter>/',
                    methods=['GET', 'POST'])
def viewclassrooms(room_filter):
    '''Display classrooms'''

    rdict = Classroom.get_free_classroom_conditions(
        **room_filter.to_kwargs())

    # partially unpack dict
    buildings = [building for building in rdict.keys()]
    timeslots = [timeslot for timeslot in rdict[buildings[0]].keys()]
    buildings.sort(key=lambda b: b.value)
    timeslots.sort(key=lambda t: t.value)

    # display all classrooms no longer used
    # no date provided, display all classrooms
    if room_filter.conds[2] is None:
        is_all = True
        # display order: building, timeslot, rooms
        info = [buildings, timeslots, rdict]
    # date provided, display free classrooms
    else:
        is_all = False
        # unpack date
        dates = [single_date for single_date in rdict[buildings[0]]
                                                     [timeslots[0]].keys()]
        dates.sort()

        # display order: date, building, timeslot, rooms
        info = [dates, buildings, timeslots, rdict]

    form = ViewClassroomsForm()

    if request.method == "POST":
        # rebuild the room_filter
        temp_filter = list(room_filter.conds)

        # this choice can no longer be selected
        if form.viewclassroom_options.data == 'all_classrooms':
            temp_filter[2] = None
        else:
            try:
                # try to match one of the keywords
                temp_filter[2] = str_to_date_dict()[form.date_options.data]
            except KeyError:
                # if its a custom entered date, do form checking
                if form.check():
                    if form.date_options.data == 'singledate':
                        temp_filter[2] = form.date_select_start.data
                    elif form.date_options.data == 'daterange':
                        temp_filter[2] = (form.date_select_start.data,
                                          form.date_select_end.data)
                else:
                    # form check failed, render template again with error msg
                    return render_template('reservation/viewroom.html.j2',
                                           is_viewroom=True,
                                           room_filter=room_filter,
                                           is_all=is_all,
                                           info=info,
                                           today=today(),
                                           form=form)

        room_filter.conds = tuple(temp_filter)

        return redirect(url_for('.viewclassrooms', room_filter=room_filter))

    # preserve form selections from the previous session
    if room_filter.conds[2] is None:
        form.viewclassroom_options.process_data('all_classrooms')
    else:
        form.viewclassroom_options.process_data('free_classrooms')
        try:
            str = date_to_str_dict()[room_filter.conds[2]]
            form.date_options.process_data(str)
        except KeyError:
            if isinstance(room_filter.conds[2], date):
                form.date_select_start.process_data(room_filter.conds[2])
            else:
                form.date_options.process_data('daterange')
                form.date_select_start.process_data(room_filter.conds[2][0])
                form.date_select_end.process_data(room_filter.conds[2][1])

    return render_template('reservation/viewroom.html.j2',
                           is_viewroom=True,
                           room_filter=room_filter,
                           is_all=is_all,
                           info=info,
                           today=today(),
                           form=form)


@resblueprint.route('/<reservation>', methods=['GET', 'POST'])
@get_callsign_decorator(Reservation, 'reservation')
def reservationinfo(reservation):
    '''Information page for a reservation'''
    # determine privileges
    is_admin = False
    is_owner = False
    is_teacher = False
    is_director = False

    if current_user.is_authenticated:
        if current_user.type == UserType.CLASSROOM_ADMIN or \
                current_user.type == UserType.DIRECTOR:
            is_admin = True

        if current_user.type == UserType.DIRECTOR:
            is_director = True

        if current_user.type == UserType.TEACHER:
            is_teacher = True

        if current_user == reservation.owner:
            is_owner = True

    # set default value to current value
    SBAppStatus_form = ChangeSBStatusForm(
        changeStatus=reservation.SBApp_status.name.lower())

    directors_approval_form = ChangeDirectorsApprovalForm(
        changeDApproval=str(reservation.directors_approval)
    )

    instructors_approval_form = ChangeInstructorsApprovalForm(
        changeIApproval=str(reservation.instructors_approval)
    )

    if request.method == 'POST':
        if SBAppStatus_form.submit.data:
            reservation.SBApp_status = \
                SBAppStatus[SBAppStatus_form.changeStatus.data.upper()]

        if directors_approval_form.submit.data:
            reservation.directors_approval = (
                True
                if directors_approval_form.changeDApproval.data == 'True'
                else False)

        if instructors_approval_form.submit.data:
            reservation.instructors_approval = (
                True
                if instructors_approval_form.changeIApproval.data == 'True'
                else False)

        return redirect(url_for('.reservationinfo',
                                reservation=reservation.callsign))

    return render_template('reservation/resinfo.html.j2',
                           is_admin=is_admin,
                           is_owner=is_owner,
                           is_teacher=is_teacher,
                           is_director=is_director,
                           SBAppStatus_form=SBAppStatus_form,
                           directors_approval_form=directors_approval_form,
                           instructors_approval_form=instructors_approval_form)


@resblueprint.route('/new/club/<club>', methods=['GET', 'POST'])
@get_callsign_decorator(Club, 'club')
@special_access_required
def newreservation_club(club):
    '''For clubs to create new reservations'''

    form = NewReservationForm()

    can_reserve = club.reservation_allowed
    if not can_reserve:
        form.submit.render_kw = {'disabled': 'disabled'}

    can_SB = club.smartboard_allowed

    if request.method == 'POST':
        if form.check():
            res = Reservation.new()

            res.status = ResStatus.UNPAIRED

            res.date = form.date_selection.data
            res.date_of_reservation = today()
            res.activity_name = ""
            res.reserver_name = club.name
            res.reserver_club = club
            res.owner = current_user

            building = Building[form.building.data.upper()]
            timeslot = ActivityTime[form.timeslot.data.upper()]
            res.timeslot = timeslot
            room_number = form.free_classrooms.data
            classrooms = Classroom.get_classroom_conditions(
                buildings=building,
                timeslot=timeslot)
            for room in classrooms:
                if room_number == room.room_number:
                    classroom = room
            if classroom is None:
                abort(500)
            res.classroom = classroom

            res.SBNeeded = False
            res.SBAppDesc = None
            res.SBApp_status = SBAppStatus.NA
            if can_SB:
                if form.SBNeeded.data == 'yes':
                    res.SBNeeded = True
                    res.SBAppDesc = form.SBAppDesc.data
                    res.SBApp_status = SBAppStatus.PENDING

            res.activity = None
            res.instructors_approval = False
            res.directors_approval = False

            res.create()

            return redirect(url_for('.reservationinfo',
                                    reservation=res.callsign))

        else:
            return render_template('reservation/newres_club.html.j2',
                                   form=form,
                                   can_reserve=can_reserve,
                                   can_SB=can_SB)

    return render_template('reservation/newres_club.html.j2',
                           form=form,
                           can_reserve=can_reserve,
                           can_SB=can_SB)


@resblueprint.route('/update_free_classrooms', methods=['POST'])
def update_free_classrooms():
    '''Dynamically provides a list of free classrooms using jQuery'''

    # get form data
    building = Building[request.form.get('building').upper()]
    timeslot = ActivityTime[request.form.get('timeslot').upper()]
    single_date = int_to_dateobj(
        int(request.form.get('date_selection').replace('-', '')))

    rdict = Classroom.get_free_classroom_conditions(
        buildings=building,
        timeslot=timeslot,
        dates=single_date)

    free_classrooms = rdict[building][timeslot][single_date]

    if free_classrooms:
        choices = [(r.room_number, r.room_number) for r in free_classrooms]
    else:
        choices = [('none', 'None available')]

    # update the choices on the client side
    return jsonify(choices)


@resblueprint.route('/viewres/club/<club>',  methods=['GET', 'POST'])
@get_callsign_decorator(Club, 'club')
def viewreservations_club(club):
    is_admin = False
    is_owner = False

    if current_user.is_authenticated:
        if current_user.type == UserType.CLASSROOM_ADMIN or \
                current_user.type == UserType.DIRECTOR:
            is_admin = True

        if current_user == club.leader:
            is_owner = True

    res = Reservation.get_reservations_conditions(
        reserver_club=club)

    canReserveForm = ChangeCanReservationForm(
        changeCanReserve=str(club.reservation_allowed))
    canSBForm = ChangeCanSmartboardForm(
        changeCanSB=str(club.smartboard_allowed))

    if request.method == 'POST':
        if canReserveForm.submit.data:
            club.reservation_allowed = \
                canReserveForm.changeCanReserve.data == 'True'

        if canSBForm.submit.data:
            club.smartboard_allowed = \
                canSBForm.changeCanSB.data == 'True'

        return redirect(url_for('.viewreservations_club', club=club.callsign))

    return render_template('reservation/viewres_club.html.j2',
                           res=res,
                           is_admin=is_admin,
                           is_owner=is_owner,
                           canReserveForm=canReserveForm,
                           canSBForm=canSBForm)


@resblueprint.route('/<reservation>/delete')
@get_callsign_decorator(Reservation, 'reservation')
def deletereservation(reservation):
    club = reservation.reserver_club
    single_date = reservation.date
    timeslot = reservation.timeslot
    building = reservation.classroom.building
    room_number = reservation.classroom.room_number
    owner = current_user

    if reservation.status == ResStatus.UNPAIRED:
        pass
    elif reservation.status == ResStatus.PAIRED:
        reservation.activity.reservation = None

    try:
        ret = Reservation.delete_reservation(single_date,
                                             timeslot,
                                             building,
                                             room_number,
                                             owner)
    except NoRow:
        abort(500)

    if ret > 1:
        abort(500)

    return redirect(url_for('.viewreservations_club', club=club.callsign))
