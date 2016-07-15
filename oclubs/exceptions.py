#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""oclubs exceptions."""


class NoRow(Exception):
    """Exception occuring when no row is found from the database."""
    pass


class AlreadyExists(Exception):
    """Exception occuring when a row exists already when inserting."""
    pass
