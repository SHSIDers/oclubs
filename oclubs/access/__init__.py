#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""oclubs Module."""

from __future__ import absolute_import

from oclubs.access import secrets
from oclubs.access import fs
from oclubs.access import database
from oclubs.access import elasticsearch
from oclubs.access import email
from oclubs.access import redis
from oclubs.access import siteconfig
from oclubs.access.delay import _done as delay_done


def done(commit=True):
    """
    Finish a request.

    :param bool commit: If true, save the data; else discard it.
    """
    database._done(commit)
    redis._done(commit)
    fs._done(commit)
    siteconfig._done(commit)
    delay_done(commit)


__all__ = [
    'fs', 'database', 'elasticsearch', 'secrets', 'email',
    'siteconfig', 'redis', 'done'
]
