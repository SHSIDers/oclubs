#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""oclubs.shsid.org Module."""

from __future__ import absolute_import

from oclubs.access import database
# TODO redis
from oclubs.access import elasticsearch


def done(commit=True):
    database.done(commit)


__all__ = ['database', 'elasticsearch', 'done']
