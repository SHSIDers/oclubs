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
        r'^\s*(\d+)(?:\s*[(-_/\\]\s*|\s+)(\d+)\s*(?:\)\s*)?(?:[AB]\s*)?$')


with open(sys.argv[1], 'r') as f:
    contents = read_xlsx(f, 'Students', ['gnumber_id', 'passport_name', 'gradeclass'])

DBstudents = User.allusers()

for DBstudent in DBstudents:
	if DBstudent.type != UserType.STUDENT:
		DBstudents.remove(DBstudent)

for DBstudent in DBstudents:
	found = False
	for student in contents:
		gnumber_id, passport_name, gradeclass = student
		if DBstudent.studentid == str(gnumber_id):
			found = True
			DBstudent.studentid == gnumber_id
			DBstudent.gnumber_id == gnumber_id
#			DBstudent.short_id = short_id
			DBstudent.passportname = passport_name
			_grade = GRADECLASSREGEX.match(gradeclass).group(1)
			_class = GRADECLASSREGEX.match(gradeclass).group(2)
			DBstudent.grade = _grade
			DBstudent.currentclass = _class
			contents.remove(student)
			print("Found:",gnumber_id, file=sys.stderr)
			break
	if not found:
		DBstudent.grade = -1
		DBstudent.currentclass = -1
		DBstudent.password = None
		DBstudent.initalized = False
		print("Not Found:", gnumber_id, file=sys.stderr)


print(len(contents), file=sys.stderr)
for student in contents:
	gnumber_id, passport_name, gradeclass = student
	u = User.new()
	u.initalized = False
	u.studentid = gnumber_id
	u.passportname = passport_name
	u.gnumber_id = gnumber_id
#	u.short_id = short_id
	_grade = GRADECLASSREGEX.match(gradeclass).group(1)
	_class = GRADECLASSREGEX.match(gradeclass).group(2)
	u.grade = _grade
	u.currentclass = _class
	u.phone = None
	u.email = ''
	u.nickname = passport_name
	u.password = None
	u.type = UserType.STUDENT
	u.picture = Upload(-1)
	u.create()
	print("Created:",gnumber_id, file=sys.stderr)

