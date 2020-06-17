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

def asciistrip(name):
    noascii=''
    for i in name:
        if ord(i)>=0 and ord(i)<=127:
            noascii+=i
    return noascii

def validate(contents):
    DBstudentsprelim = User.allusers()
    DBstudents = [x for x in DBstudentsprelim if x.type == UserType.STUDENT]
    invalids = []
    log=''
    for DBstudent in DBstudents:
        validid = False
        if DBstudent.studentid!=None and DBstudent.studentid[0]=='G':
            DBstudent.gnumber_id=DBstudent.studentid
            validid=True
        elif DBstudent.gnumber_id!=None and DBstudent.gnumber_id[0]=='G':
            DBstudent.studentid=DBstudent.gnumber_id
            validid=True
        if validid and DBstudent.grade!=-1:
            log+="Student:"+DBstudent.gnumber_id+DBstudent.passportname+DBstudent.grade+DBstudent.currentclass+'\n'
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
                log+="Student No Longer Present:"+DBstudent.gnumber_id+'\n'
        elif not validid and DBstudent.grade!=-1:
            log+="Invalid ID fix?:"+DBstudent.gnumber_id+'\n'
    return log

def newstudents(contents):
    log=''
    DBstudentsprelim = User.allusers()
    DBstudents = [x for x in DBstudentsprelim if x.type == UserType.STUDENT]
    for DBstudent in DBstudents:
        for student in contents:
            gnumber_id, passport_name, gradeclass = student
            if DBstudent.studentid == str(gnumber_id):
                log+="Error student's G# already exists"
                contents.remove(student)
    for student in contents:
        gnumber_id, passport_name, gradeclass = student
        log+="Student:"+gnumber_id+passport_name+gradeclass+'\n'
        try:
            u = User.new()
            u.initalized = False
            u.studentid = gnumber_id
            u.passportname = asciistrip(passport_name)
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
            log+="Created:"+gnumber_id+'\n'
        except:
            log+='Failed:'+gnumber_id+'\n'
    return log