#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""
Module to send emails.

This module sends emails with either Postfix or SendGrid.
"""

from __future__ import absolute_import, unicode_literals

import traceback

from envelopes import Envelope, SMTP

from oclubs.access.delay import delayed_func

from_email = ('no-reply@oclubs.shs.cn', 'Connect')


@delayed_func
def send(to_email, subject, content):
    """
    Send an email.

    :param tuple to_email: email recipient address and name
    :param basestring subject: email subject
    :param basestring content: email content
    """

    try:
        conn = SMTP('127.0.0.1', 25)
        mail = Envelope(
            to_addr=to_email[0],
            from_addr=from_email,
            subject=subject,
            text_body=content
        )
        conn.send(mail)
    except Exception:
        traceback.print_exc()
