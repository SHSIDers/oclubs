#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from enum import Enum


class UserType(Enum):
    STUDENT = 1
    TEACHER = 2
    ADMIN = 3

    @property
    def format_name(self):
        return ['', 'Student', 'Teacher', 'Admin'][self.value]


class ClubType(Enum):
    ACADEMICS = 1
    SPORTS = 2
    ARTS = 3
    SERVICES = 4
    ENTERTAINMENT = 5
    OTHERS = 6
    SCHOOL_TEAMS = 7

    @property
    def format_name(self):
        return ['', 'Academics', 'Sports', 'Arts', 'Services',
                'Entertainment', 'Others', 'School Teams'][self.value]


class ActivityTime(Enum):
    UNKNOWN = 0
    NOON = 1
    AFTERSCHOOL = 2
    HONGMEI = 3
    OTHERS = 4

    @property
    def format_name(self):
        return ['Unknown', 'Noon', 'Afterschool', 'HongMei',
                'Others'][self.value]


class ClubJoinMode(Enum):
    FREE_JOIN = 1
    BY_INVITATION = 2

    @property
    def format_name(self):
        return ['', 'Free Join', 'By Invitation'][self.value]

__all__ = ['UserType', 'ClubType', 'ActivityTime', 'ClubJoinMode']
