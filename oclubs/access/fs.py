#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

import os
import shutil

from flask import g


def done(commit=True):
    if g.get('fsWatchingFiles', None):
        if not commit:
            for path in g.fsWatchingFiles:
                if os.path.isdir(path) and not os.path.islink(path):
                    shutil.rmtree(path)
                elif os.path.exists(path):
                    os.remove(path)

        g.fsWatchingFiles = None
        del g.fsWatchingFiles


def watch(path):
    if path:
        g.fsWatchingFiles = g.get('fsWatchingFiles', [])
        g.fsWatchingFiles.append(path)
