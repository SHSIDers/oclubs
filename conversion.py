#! /usr/local/bin/pyshell
# -*- coding: UTF-8 -*-

from oclubs.shared import read_xlsx

with open('/srv/oclubs/oclubs/example.md', 'r') as f:

    contents = read_xlsx(f, 'Students', ['studentid', 'passportname', 'grade', 'class'])

    authority = {}
    for student in contents:
        studentid, passportname, grade, curclass = student
        authority[studentid] = {
            'UNIONID': studentid,
            'NAMEEN': passportname,
            'GRADENAME': grade,
            'STUCLASSNAME': curclass,
        }

    from oclubs.worker import refresh_user
    refresh_user.delay(authority)
