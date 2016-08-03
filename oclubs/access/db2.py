#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import

from ibm_db import connect, fetch_assoc, exec_immediate

from oclubs.access import get_secret


def _results(command):
    ret = []
    result = fetch_assoc(command)
    while result:
        ret.append(result)
        result = fetch_assoc(command)
    return ret


def _execute(sql):
    connection = connect(get_secret('db2_conn'), '', '')
    return _results(exec_immediate(connection, sql))


def allstudents():
    return _execute("SELECT * FROM cwshs.v_student_all2 WHERE "
                    "deleted = 0 AND gradename IN ('9', '10', '11', '12')")
