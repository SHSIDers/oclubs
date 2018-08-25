#! /usr/local/bin/pyshell
# -*- coding: UTF-8 -*-
#

import argparse
import getpass
import readline  # noqa
import sys
import traceback

from oclubs.objs.user import _encrypt


if False:
    # to trick flake8 into thinking things are defined
    Upload = User = UserType = type('Magic', (object,), {})
    done = (lambda: None)

parser = argparse.ArgumentParser(
    description='Manually create a new oClubs user.')
parser.add_argument('--type',
                    choices=UserType.__members__.keys(),
                    required=True)

args = parser.parse_args()


def noblank(prompt):
    while True:
        ret = raw_input(prompt)
        if not ret:
            print >> sys.stderr, 'Cannot be blank!'
            continue
        else:
            return ret


def defaults(prompt, default):
    return raw_input(prompt % default) or default


typ = UserType[args.type]

if typ == UserType.TEACHER:
    print >> sys.stderr, 'Teacher accounts are dynamically created upon club '\
                         'creation. Only email address is needed.'
    emailaddress = noblank('Email accress: ')
    u = User.find_teacher(emailaddress)
else:
    u = User.new()

    u.studentid = noblank('Student ID: ')
    u.passportname = noblank('Real/Passport name (login username): ')

    while True:
        password = getpass.getpass('Password (will not be shown): ')
        # Try encrypting
        try:
            _encrypt(password)
        except:
            traceback.print_exc()
            continue
        password_repeat = getpass.getpass('Repeat password: ')
        if password != password_repeat:
            print >> sys.stderr, 'Passwords do not match!'
            continue
        else:
            u.password = password
            break

    u.nickname = defaults('Nickname [%s]: ', u.passportname)
    u.email = raw_input('Email address: ')
    u.phone = None
    u.picture = Upload(-101)
    u.type = typ
    u.initalized = False

    if typ == UserType.STUDENT:
        while True:
            try:
                u.grade, u.currentclass = User.extract_gradeclass(
                    raw_input('Grade & Class: '))
            except ValueError:
                traceback.print_exc()
                continue
            else:
                break
    else:
        u.grade = u.currentclass = None

    u.create()


done()
print 'Created User with ID ' + str(u.id)
