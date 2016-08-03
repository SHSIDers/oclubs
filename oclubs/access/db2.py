#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import

from ibm_db import close, connect, exec_immediate, fetch_assoc

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
    try:
        return _results(exec_immediate(connection, sql))
    finally:
        close(connection)


def allstudents():
    return _execute("SELECT * FROM cwshs.v_student_all2 WHERE "
                    "deleted = 0 AND gradename IN ('9', '10', '11', '12')")
