#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from ConfigParser import ConfigParser

from oclubs.access.delay import delayed_func

FILENAME = '/srv/oclubs/siteconfig.ini'


def get_config(name):
    config = ConfigParser()
    config.read(FILENAME)
    return config.getboolean('siteconfig', name)


@delayed_func
def set_config(name, value):
    config = ConfigParser()
    config.read(FILENAME)
    config.set('siteconfig', name, value)

    with open(FILENAME, 'w') as configfile:
        config.write(configfile)
