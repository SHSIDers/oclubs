#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""email module that sends email via SendGrid."""

from __future__ import absolute_import, unicode_literals

import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail
from oclubs.shared import get_secret

sg = sendgrid.SendGridAPIClient(apikey=get_secret('sendgrid_key'))
from_email = Email("no-reply@oclubs.shsid.org", "oClubs")


def _send(to_email, subject, content):
    to_email = Email(to_email)
    mail = Mail(from_email, subject, to_email, content)
    sg.client.mail.send.post(request_body=mail.get())


def send(to_emails, subject, content):
    content = Content("text/plain", content)
    if isinstance(to_emails, str):
        _send(to_emails, subject, content)
    elif isinstance(to_emails, list):
        for email in to_emails:
            _send(email, subject, content)
