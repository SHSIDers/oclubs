#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import division

import subprocess


def total_seconds(timedelta):
    return ((
        timedelta.microseconds + (
            timedelta.seconds + timedelta.days * 24 * 3600
        ) * 10**6
    ) / 10**6)


# duck punch
if not hasattr(subprocess, 'check_output'):
    def check_output(*popenargs, **kwargs):
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
        process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise subprocess.CalledProcessError(retcode, cmd)
        return output
    subprocess.check_output = check_output
