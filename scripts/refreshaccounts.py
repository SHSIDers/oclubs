#! /usr/local/bin/pyshell
# -*- coding: UTF-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
import re
import csv
import sys
import codecs
from oclubs.objs import User, Upload
from oclubs.shared import read_xlsx
from oclubs.enums import UserType

GRADECLASSREGEX = re.compile(
        r'(\d{1,2})\s*[(（-]\s*(\d{1,2})\s*[）)]\s*[AB]?')


with open('2019II.xlsx', 'r') as f:
    contents = read_xlsx(f, 'sheet1', ['gnumber_id', 'passport_name', 'gradeclass'])

DBstudentsprelim = User.allusers()

def validate():
    DBstudents = [x for x in DBstudentsprelim if x.type == UserType.STUDENT]
    invalids = []
    for DBstudent in DBstudents:
        validid = False
        if DBstudent.studentid!=None and DBstudent.studentid[0]=='G':
            DBstudent.gnumber_id=DBstudent.studentid
            validid=True
        elif DBstudent.gnumber_id!=None and DBstudent.gnumber_id[0]=='G':
            DBstudent.studentid=DBstudent.gnumber_id
            validid=True
        if validid and DBstudent.grade!=-1:
            print("Student:", DBstudent.gnumber_id, DBstudent.passportname, DBstudent.grade, DBstudent.currentclass, file=sys.stderr)
            for student in contents:
                gnumber_id, passport_name, gradeclass = student
                if DBstudent.studentid == str(gnumber_id):
                    found = True
                    DBstudent.studentid == gnumber_id
                    DBstudent.gnumber_id == gnumber_id
                    DBstudent.passportname = passport_name
                    _grade = GRADECLASSREGEX.match(gradeclass).group(1)
                    _class = GRADECLASSREGEX.match(gradeclass).group(2)
                    DBstudent.grade = int(_grade)
                    DBstudent.currentclass = int(_class)
                    contents.remove(student)
                    print("Found:",gnumber_id, file=sys.stderr)
                    break
            else:
                DBstudent.grade = -1
                DBstudent.currentclass = -1
                DBstudent.password = None
                DBstudent.initalized = False
                print("Not Found:", DBstudent.gnumber_id, file=sys.stderr)
        elif not validid and DBstudent.grade!=-1:
            invalids.append("Invalid ID fix?:", DBstudent.gnumber_id, file=sys.stderr)
    for x in invalids:
        print(x)

validate()

print(len(contents), file=sys.stderr)
for student in contents:
    gnumber_id, passport_name, gradeclass = student
    print("Student:", gnumber_id, passport_name, gradeclass, file=sys.stderr)
    u = User.new()
    u.initalized = False
    u.studentid = gnumber_id
    u.passportname = passport_name
    u.gnumber_id = gnumber_id
    u.short_id = None
    _grade = GRADECLASSREGEX.match(gradeclass).group(1)
    _class = GRADECLASSREGEX.match(gradeclass).group(2)
    u.grade = int(_grade)
    u.currentclass = int(_class)
    u.phone = None
    u.email = ''
    u.nickname = passport_name
    u.password = None
    u.type = UserType.STUDENT
    u.picture = Upload(-1)
    u.create()
    print("Created:",gnumber_id, file=sys.stderr)

done()