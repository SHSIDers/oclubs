#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""
Module to access SHSID authortative database, which is currently IBM DB2.

Only accessing student data is implemented.
"""

from __future__ import absolute_import

from ibm_db import close, connect, exec_immediate, fetch_assoc

from oclubs.access.secrets import get_secret


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
    """
    Get information on all students in grade 9 - 12.

    :returns: student information, with each student a dict in the list
    :rtype: list of dict
    """
    return _execute("SELECT * FROM cwshs.v_student_all2 WHERE "
                    "deleted = 0 AND gradename IN ('9', '10', '11', '12')")
