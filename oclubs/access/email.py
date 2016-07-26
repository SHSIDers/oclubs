#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""email module that sends email via SendGrid."""

import sendgrid
import os
from sendgrid.helpers.mail import *

sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
from_email = Email("no-reply@oclubs.shsid.org","oClubs")


def _send(to_email, subject, content):
    to_email = Email(to_email)
    mail = Mail(from_email, subject, to_email, content)
    try:
        response = sg.client.mail.send.post(request_body=mail.get())
    except:
        print "Error occured while sending email" #FIXME

# Receives to_emails parameter either in string(single email) or in list(multiple emails)
def send(to_emails, subject, content): 
    content = Content("text/plain", content)
    if isinstance(to_emails, str):
        _send(to_emails, subject, content)
    elif isinstance(to_emails, list):
        for email in to_emails:
            _send(email, subject, content)
    raise RuntimeError("invalid to_emails parameter")
