#! /usr/local/bin/pyshell
# -*- coding: UTF-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
import sys
import codecs
from oclubs.objs import Reservation,  Classroom
from oclubs.enums import UserType




cs=[ {'r':'107', 'l': 0, 'a': 1, 'd': 'Large classroom'},
{'r':'105', 'l': 0, 'a': 1, 'd': 'Large classroom'},
{'r':'111', 'l': 0, 'a': 1, 'd': 'Large classroom'},
{'r':'113', 'l': 0, 'a': 1, 'd': 'Large classroom'},
{'r':'201', 'l': 1, 'a': 0, 'd': ''},
{'r':'202', 'l': 1, 'a': 0, 'd': ''},
{'r':'203', 'l': 1, 'a': 0, 'd': ''},
{'r':'204', 'l': 1, 'a': 0, 'd': ''},
{'r':'205', 'l': 1, 'a': 0, 'd': ''},
{'r':'206', 'l': 1, 'a': 0, 'd': ''},
{'r':'207', 'l': 1, 'a': 0, 'd': ''},
{'r':'208', 'l': 1, 'a': 0, 'd': ''},
{'r':'216', 'l': 1, 'a': 0, 'd': ''},
{'r':'217', 'l': 1, 'a': 0, 'd': ''},
{'r':'218', 'l': 1, 'a': 0, 'd': ''},
{'r':'209', 'l': 1, 'a': 0, 'd': 'Large classroom'},
{'r':'211', 'l': 1, 'a': 0, 'd': 'Large classroom'},
{'r':'301', 'l': 1, 'a': 1, 'd': ''},
{'r':'302', 'l': 1, 'a': 1, 'd': ''},
{'r':'303', 'l': 1, 'a': 1, 'd': ''},
{'r':'305', 'l': 1, 'a': 1, 'd': ''},
{'r':'306', 'l': 1, 'a': 1, 'd': ''},
{'r':'307', 'l': 1, 'a': 1, 'd': ''},
{'r':'308', 'l': 1, 'a': 1, 'd': ''},
{'r':'215', 'l': 0, 'a': 1, 'd': ''},
{'r':'315', 'l': 1, 'a': 0, 'd': ''},
{'r':'316', 'l': 1, 'a': 1, 'd': ''},
{'r':'317', 'l': 1, 'a': 1, 'd': ''},
{'r':'318', 'l': 1, 'a': 1, 'd': ''},
{'r':'309', 'l': 1, 'a': 1, 'd': 'Large classroom'},

]

res = Reservation.delete_reservation()
cls = Classroom.delete_all_classrooms(building=2)

for i in cs:
    c = Classroom.new()
    c.room_number = i['r']
    c.studentsToUseLunch = i['l']
    c.studentsToUseAfternoon = i['a']
    c.building = 2
    c.desc = i['d']
    c.create()
    print("Created:",i['r'],i['l'],i['a'],i['d'])
done()