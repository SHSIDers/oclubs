#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""Module to read from screts.ini."""

from ConfigParser import ConfigParser


def get_secret(name):
    """
    Read a secret from secrets.ini.

    :param basestring name: name of the secret
    :returns: value of the secret
    :rtype: basestring
    """
    config = ConfigParser()
    config.read('/srv/oclubs/secrets.ini')
    return config.get('secrets', name)
