#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""
Module to send emails.

This module sends emails with either Postfix or SendGrid.
"""

from __future__ import absolute_import, unicode_literals

import traceback

import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail

from oclubs.access.secrets import get_secret
from oclubs.access.delay import delayed_func

from_email = ('no-reply@connect.shs.cn', 'Connect')


@delayed_func
def send(to_email, subject, content):
    """
    Send an email.

    :param tuple to_email: email recipient address and name
    :param basestring subject: email subject
    :param basestring content: email content
    """

    if not get_secret('sendgrid_key'):
        # This is a test machine
        return

    try:
        sg = sendgrid.SendGridAPIClient(apikey=get_secret('sendgrid_key'))
        content = Content('text/plain', content)
        mail = Mail(Email(*from_email), subject, Email(to_email[0]), content)
        sg.client.mail.send.post(request_body=mail.get())
    except Exception:
        traceback.print_exc()
