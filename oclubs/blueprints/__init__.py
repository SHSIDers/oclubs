#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""oclubs Module."""

from __future__ import absolute_import

from oclubs.blueprints.actblueprint import actblueprint
from oclubs.blueprints.clubblueprint import clubblueprint
from oclubs.blueprints.userblueprint import userblueprint
from oclubs.blueprints.resblueprint import resblueprint

__all__ = ['actblueprint', 'clubblueprint', 'userblueprint', 'resblueprint']
