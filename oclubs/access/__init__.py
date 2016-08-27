#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""oclubs Module."""

from __future__ import absolute_import

from oclubs.access.secrets import get_secret
from oclubs.access import fs
from oclubs.access import database
from oclubs.access import db2
from oclubs.access import elasticsearch
from oclubs.access import email
from oclubs.access import redis
from oclubs.access.delay import done as delay_done


def done(commit=True):
    database.done(commit)
    redis.done(commit)
    fs.done(commit)
    delay_done(commit)


__all__ = [
    'fs', 'database', 'db2', 'elasticsearch', 'get_secret', 'email', 'redis',
    'done'
]
