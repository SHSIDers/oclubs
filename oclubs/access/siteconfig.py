#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from ConfigParser import ConfigParser

from flask import g

FILENAME = '/srv/oclubs/siteconfig.ini'


def done(commit=True):
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
    return _get_parser().getboolean('siteconfig', name)


def set_config(name, value):
    # ConfigParser stores bool in memory, and getboolean expects string
    _get_parser().set('siteconfig', name, str(int(value)))
    g.siteconfigHasWrites = True
