#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

from functools import wraps

from flask import g


def done(commit=True):
    if g.get('delayedFunc', None):
        if commit:
            for func, args, kwargs in g.delayedFunc:
                func(*args, **kwargs)
        g.delayedFunc = None
        del g.delayedFunc


def delayed_func(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        g.delayedFunc = g.get('delayedFunc', [])
        g.delayedFunc.append((func, args, kwargs))

    return decorated_function
