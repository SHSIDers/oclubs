#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import unicode_literals, absolute_import, division

from flask import *

from oclubs import *
from oclubs.app import *
from oclubs.access import *
from oclubs.enums import *
from oclubs.objs import *
from oclubs.shared import *

with app.app_context():
    __import__('code').interact("Welcome to the oClubs interactive shell!",
                                local=locals())
