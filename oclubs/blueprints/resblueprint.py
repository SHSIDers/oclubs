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
from oclubs.objs import Reservation, Activity, User, Club

resblueprint = Blueprint('resblueprint', __name__)
