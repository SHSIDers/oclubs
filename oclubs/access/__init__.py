#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""oclubs.shsid.org Module."""

from __future__ import absolute_import

from oclubs.access import database
# TODO redis
# TODO elasticsearch


def done(commit=True):
    database.done(commit)


__all__ = ['database', 'done']
