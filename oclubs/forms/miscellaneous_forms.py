#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals, division

from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, SubmitField, HiddenField
from wtforms.fields.html5 import EmailField

from oclubs.objs import User


class LoginForm(FlaskForm):
    username = TextField(
        'Username',
    )

    password = PasswordField(
        'Password',
    )

    password_2 = PasswordField(
        'Password',
    )

    email = EmailField(
        'Email'
    )

    submit = SubmitField(
        'Login',
    )

    is_initalized = HiddenField(
        default='false'
    )
    is_firstPass = HiddenField(
        default='true'
    )

    nexturl = HiddenField()

    forgotpassword = SubmitField(
        'Forgot password'
    )

    def check(self):
        # username is always checked for validity
        if self.username.data is None or self.username.data == '':
            self.errors[self.username] = 'Please enter a username.'
            return False

        if User.get_userobj_from_loginname(self.username.data) is None:
            self.errors[self.username] = 'Username doesn\'t exist.'
            return False

        # first pass
        if self.is_firstPass.data == 'true':
            pass
        # second pass
        else:
            if (not self.forgotpassword.data and
                    (self.password.data is None or self.password.data == '')):
                self.errors[self.password] = 'Please enter a password lol.'
                return False

            # initalization checking
            if self.is_initalized.data == 'false':
                if self.password.data != self.password_2.data:
                    self.errors[self.password_2] = 'Passwords do not match.'
                    return False

                if len(self.password.data) < 6:
                    self.errors[self.password] = 'Password is too short.'
                    return False

                if self.email.data is None or self.email.data == '':
                    self.errors[self.email] = 'Please enter an email.'
                    return False

            else:
                pass

        return True
