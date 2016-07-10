#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""oclubs exceptions."""


class NoRow(Exception):
    """Exception occuring when no row is fund fron the database."""

    def __init__(self):
        """Initialize."""
        super(NoRow, self).__init__()
