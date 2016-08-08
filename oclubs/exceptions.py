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


class UploadNotSupported(Exception):
    """Exception occuring when an uploaded file is not supported."""
    pass


class PasswordTooShort(Exception):
    """Exception occuring someone sets a password that's too short."""
    pass
