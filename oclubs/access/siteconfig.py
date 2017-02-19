#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""Module to access site configuration in siteconfig.ini."""


from ConfigParser import ConfigParser

from flask import g

FILENAME = '/srv/oclubs/siteconfig.ini'


def _done(commit=True):
    if g.get('siteconfigParser', None):
        if commit:
            if g.get('siteconfigHasWrites', False):
                with open(FILENAME, 'w') as configfile:
                    g.siteconfigParser.write(configfile)
        g.siteconfigParser = None
        del g.siteconfigParser
        g.siteconfigHasWrites = None
        del g.siteconfigHasWrites


def _get_parser():
    if g.get('siteconfigParser', None):
        return g.siteconfigParser

    g.siteconfigParser = ConfigParser()
    g.siteconfigParser.read(FILENAME)
    return g.siteconfigParser


def get_config(name):
    """
    Get a site configuration boolean.

    :param basestring name: name of site configuration
    :returns: value of site configuration
    :rtype: bool
    """
    return _get_parser().getboolean('siteconfig', name)


def set_config(name, value):
    """
    Set a site configuration boolean.

    :param basestring name: name of site configuration
    :param bool value: new value of site configuration
    """
    # ConfigParser stores bool in memory, and getboolean expects string
    _get_parser().set('siteconfig', name, str(int(value)))
    g.siteconfigHasWrites = True
