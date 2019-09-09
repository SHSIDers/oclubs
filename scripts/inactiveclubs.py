#! /usr/local/bin/pyshell
# -*- coding: UTF-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
import sys
import codecs
from oclubs.objs import Reservation,  Classroom
from oclubs.enums import Building

DBclubs = Club.allclubs(grade_limit = (9,10))

for i in DBclubs:
    i.smartboard_allowed = 0
    i.is_active = 0
done()