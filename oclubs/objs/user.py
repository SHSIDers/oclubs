#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""oclubs.shsid.org Users."""

from __future__ import absolute_import

from oclubs.access import database


class User(object):
    """User class."""

    def __init__(self, uid):
        """Initializer."""
        super(User, self).__init__()
        self.uid = uid
        self.data = {}

    def load_db(self):
        """Load data from db."""
        # TODO
        self.data = database()
