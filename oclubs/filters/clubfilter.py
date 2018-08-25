#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

import re

from flask import abort
from werkzeug.routing import PathConverter

from oclubs.enums import ClubType


class ClubFilter(object):
    DEFAULT = (False, None, None)
    GRADE_REGEX = re.compile(r'([01]?[0-9])-([01]?[0-9])')

    def __init__(self, conds=None, is_single_club=False):
        self.conds = self.DEFAULT if conds is None else conds
        self.is_single_club = is_single_club

    @classmethod
    def from_url(cls, url):
        excellent, typ, grade = cls.DEFAULT
        if url and url != 'all':
            for cond in url.split('/'):
                if cond == 'excellent':
                    excellent = True
                else:
                    try:
                        typ = ClubType[cond.upper()]
                        continue
                    except KeyError:
                        pass

                    reobj = cls.GRADE_REGEX.match(cond)
                    if reobj:
                        grade = range(int(reobj.group(1)),
                                      int(reobj.group(2)) + 1)
                        continue

                        abort(404)

        return cls((excellent, typ, grade))

    @classmethod
    def from_club(cls, club):
        grade = [0, 1] if club.leader.grade % 2 else [-1, 0]
        grade = map(lambda x: x + club.leader.grade, grade)
        return cls((club.is_excellent, club.type, grade), is_single_club=True)

    def to_url(self):
        return self.build_url(self.conds)

    def to_kwargs(self):
        ret = {}
        excellent, typ, grade = self.conds
        if excellent:
            ret['excellent_only'] = True
        if typ:
            ret['club_types'] = [typ]
        if grade:
            ret['grade_limit'] = grade

        return ret

    @classmethod
    def build_url(cls, conds):
        if conds == cls.DEFAULT:
            return 'all'

        excellent, typ, grade = conds
        return '/'.join(filter(None, (
            'excellent' if excellent else None,
            typ.name.lower() if typ else None,
            '%d-%d' % (grade[0], grade[-1]) if grade else None
        )))

    def toggle_url(self, cond):
        excellent, typ, grade = self.conds
        if cond in ['all', 'excellent']:
            return self.build_url((['all', 'excellent'].index(cond),
                                   typ, grade))
        else:
            try:
                newtyp = ClubType[cond.upper()]
            except KeyError:
                pass
            else:
                return self.build_url((excellent,
                                      newtyp if newtyp != typ else None,
                                      grade))

            reobj = self.GRADE_REGEX.match(cond)
            newgrade = range(int(reobj.group(1)),
                             int(reobj.group(2)) + 1)
            return self.build_url((excellent, typ,
                                  newgrade if newgrade != grade else None))

    def enumerate(self):
        return [
            {
                'name': 'Achievement',
                'elements': [
                    {'url': 'all', 'name': 'All Clubs',
                     'selected': not self.conds[0]},
                    {'url': 'excellent', 'name': 'Excellent Clubs',
                     'selected': self.conds[0]}
                ]
            },
            {
                'name': 'Club Types',
                'elements': [
                    {'url': t.name.lower(), 'name': t.format_name,
                     'selected': self.conds[1] == t}
                    for t in ClubType
                ]
            },
            {
                'name': 'Grades',
                'elements': [
                    {'url': '9-10', 'name': 'Grade 9 - 10',
                     'selected': self.conds[2] == [9, 10]},
                    {'url': '11-12', 'name': 'Grade 11 - 12',
                     'selected': self.conds[2] == [11, 12]},
                ]
            },
        ]

    def enumerate_desktop(self):
        ret = self.enumerate()

        if not self.is_single_club:
            for group in ret:
                for elmt in group['elements']:
                    elmt['url'] = self.toggle_url(elmt['url'])

        return ret

    def enumerate_mobile(self):
        ret = []
        hasselection = False

        for group in self.enumerate():
            for elmt in group['elements']:
                if hasselection or elmt['url'] == 'all':
                    elmt['selected'] = False
                else:
                    hasselection = elmt['selected']

                ret.append(elmt)

        # all clubs
        ret[0]['selected'] = not hasselection

        return ret

    def title(self):
        excellent, typ, grade = self.conds
        return ' '.join(filter(None, (
            ['All Clubs', 'Excellent Clubs'][excellent],
            'of ' + typ.format_name if typ else None,
            'in Grade %d - %d' % (grade[0], grade[-1]) if grade else None
        )))


class ClubFilterConverter(PathConverter):
            def to_python(self, value):
                return ClubFilter.from_url(value)

            def to_url(self, value):
                try:
                    return value.to_url()
                except AttributeError:
                    return value
