#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from enum import Enum


class UserType(Enum):
    STUDENT = 1
    TEACHER = 2
    ADMIN = 3


class ClubType(Enum):
    ACADEMICS = 1
    SPORTS = 2
    ARTS = 3
    SERVICES = 4
    ENTERTAINMENT = 5
    OTHERS = 6
    SCHOOL_TEAMS = 7


class ActivityTime(Enum):
    UNKNOWN = 0
    NOON = 1
    AFTERSCHOOL = 2
    HONGMEI = 3
    OTHERS = 4


__all__ = ['UserType', 'ClubType', 'ActivityTime']
