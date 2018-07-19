#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals, division

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
from oclubs.objs import Reservation, Activity, User, Club

resblueprint = Blueprint('resblueprint', __name__)


@resblueprint.route('/<resfilter:res_filter>/', defaults={'page': 1})
@resblueprint.route('/<resfilter:res_filter>/<int:page>')
def allreservations(res_filter, page):
    '''All reservations'''
    res_num = 20
    count, res = Reservation.get_reservations_conditions(
        limit=((page-1)*res_num, res_num),
        **res_filter.to_kwargs())
    pagination = Pagination(page, res_num, count)
    return render_template('reservation/allres.html.j2',
                           res=res,
                           pagination=pagination,
                           res_filter=res_filter)
