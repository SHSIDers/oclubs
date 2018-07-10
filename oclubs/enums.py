#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""oClubs enums."""

from enum import Enum


class UserType(Enum):
    """Enum regarding the type of a user."""
    STUDENT = 1
    TEACHER = 2
    ADMIN = 3 #legacy
    CLUB_ADMIN = 4
    CLASSROOM_ADMIN = 5
    DIRECTOR = 6


    @property
    def format_name(self):
        """Formats the value of the enum for display."""
        return ['', 'Student', 'Teacher', 'Admin',
                'Club Administrator','Classroom Reservation Administrator',
                'Director'][self.value]


class ClubType(Enum):
    """Enum regarding the type of a club."""
    ACADEMICS = 1
    SPORTS = 2
    ARTS = 3
    SERVICES = 4
    ENTERTAINMENT = 5
    OTHERS = 6
    SCHOOL_TEAMS = 7

    @property
    def format_name(self):
        """Formats the value of the enum for display."""
        return ['', 'Academics', 'Sports', 'Arts', 'Services',
                'Entertainment', 'Others', 'School Teams'][self.value]


class ActivityTime(Enum):
    """Enum regarding the time of an activity."""
    UNKNOWN = 0
    NOON = 1
    AFTERSCHOOL = 2
    HONGMEI = 3
    OTHERS = 4

    @property
    def format_name(self):
        """Formats the value of the enum for display."""
        return ['Unknown', 'Noon', 'Afterschool', 'HongMei',
                'Others'][self.value]


class ClubJoinMode(Enum):
    """Enum regarding the join mode of a club."""
    FREE_JOIN = 1
    BY_INVITATION = 2

    @property
    def format_name(self):
        """Formats the value of the enum for display."""
        return ['', 'Free Join', 'By Invitation'][self.value]

class Building(Enum):
    """Enum for buildings for classroom reservation."""
    XMT = 1

    @property
    def format_name(self):
        """Formats the value of the enum for display."""
        return ['','XMT'][self.value]

__all__ = ['UserType', 'ClubType', 'ActivityTime', 'ClubJoinMode', 'Building']
