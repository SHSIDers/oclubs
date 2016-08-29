#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

import traceback

from envelopes import Envelope, SMTP
import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail

from oclubs.access import get_secret
from oclubs.access.delay import delayed_func

from_email = ('no-reply@oclubs.shs.cn', 'oClubs')


@delayed_func
def send(to_email, subject, content):
    if not get_secret('sendgrid_key'):
        # This is a test machine
        return

    try:
        if to_email[0].endswith('@gmail.com'):
            sg = sendgrid.SendGridAPIClient(apikey=get_secret('sendgrid_key'))
            content = Content('text/plain', content)
            mail = Mail(Email(*from_email), subject, Email(to_email[0]), content)
            sg.client.mail.send.post(request_body=mail.get())
        else:
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
