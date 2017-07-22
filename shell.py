#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import unicode_literals, absolute_import, division

import os
import sys

from flask import *

from oclubs import *
from oclubs.app import *
from oclubs.access import *
from oclubs.enums import *
from oclubs.objs import *
from oclubs.shared import *

with app.test_request_context('/', method='GET'):
    if len(sys.argv) == 1:
        if sys.stdin.isatty():
            __import__('code').interact(
                "Welcome to the oClubs interactive shell!",
                local=locals())
        else:
            exec sys.stdin.read()
    else:
        del sys.argv[0]
        execfile(sys.argv[0])
        # print >> sys.stderr, 'Invalid number of arguments!'
        # sys.exit(1)
