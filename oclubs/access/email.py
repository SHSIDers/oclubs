#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

from envelopes import Envelope, SMTP

conn = SMTP('127.0.0.1', 25)
from_email = ('no-reply@oclubs.shsid.org', 'oClubs')


def send(to_email, subject, content):
    mail = Envelope(
        to_addr=to_email,
        from_addr=from_email,
        subject=subject,
        text_body=content
    )
    conn.send(mail)
