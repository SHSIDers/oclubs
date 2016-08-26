#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

from flask import g
from envelopes import Envelope, SMTP
import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail

from oclubs.access import get_secret

from_email = ('no-reply@oclubs.shsid.org', 'oClubs')


def done(commit=True):
    if g.get('emailsToSend', None):
        if commit:
            for args, kwargs in g.emailsToSend:
                _send(*args, **kwargs)
        g.emailsToSend = None
        del emailsToSend


def send(*args, **kwargs):
    g.redisObjDict = g.get('redisObjDict', [])
    g.redisObjDict.append((args, kwargs))


def _send(to_email, subject, content):
    if to_email[0].endswith('@gmail.com'):
        sg = sendgrid.SendGridAPIClient(apikey=get_secret('sendgrid_key'))
        content = Content('text/plain', content)
        mail = Mail(Email(*from_email), subject, Email(*to_email), content)
        sg.client.mail.send.post(request_body=mail.get())
    else:
        conn = SMTP('127.0.0.1', 25)
        mail = Envelope(
            to_addr=to_email,
            from_addr=from_email,
            subject=subject,
            text_body=content
        )
        conn.send(mail)
