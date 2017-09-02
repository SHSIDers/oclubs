#! /usr/local/bin/pyshell
# -*- coding: UTF-8 -*-


from oclubs.shared import read_xlsx
from oclubs.access import database
from oclubs.objs import User

if False:
    # to trick flake8 into thinking things are defined
    done = (lambda: None)


with open('/SampleData.xlsx', 'r') as f:

    contents = read_xlsx(f, 'Students', ['oldid', 'newid', 'passportname', 'gradeclass'])

    i = 2

    for student in contents:
        oldid, newid, passportname, gradeclass = student
        grade, curclass = User.extract_gradeclass(gradeclass)
        print i, grade, curclass
        i += 1

        try:
            data = database.fetch_oneentry(
                'user', 'user_id', {'user_login_name': oldid}
            )
        except:
            continue

        u = User(data)
        u.studentid = newid
        u.passportname = passportname
        u.nickname = passportname

done()
