#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from ConfigParser import ConfigParser


def get_secret(name):
    config = ConfigParser()
    config.read('/srv/oclubs/secrets.ini')
    return config.get('secrets', name)
