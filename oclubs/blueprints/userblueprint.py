#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

from collections import defaultdict
from datetime import date

from flask import (
    Blueprint, render_template, url_for, request, redirect, abort, flash,
    jsonify
)
from flask_login import current_user, login_required, fresh_login_required

from oclubs.objs import User, Club, Upload
from oclubs.enums import UserType, ActivityTime
from oclubs.shared import (
    special_access_required, download_xlsx, render_email_template, Pagination,
    fail
)
from oclubs.exceptions import PasswordTooShort
from oclubs.access import siteconfig, email

userblueprint = Blueprint('userblueprint', __name__)


@userblueprint.route('/')
@login_required
def personal():
    '''Student Personal Page'''
    pictures = [Upload(-num) for num in range(1, 21)]
    allow_club_creation = siteconfig.get_config('allow_club_creation')
    receive_email = current_user.get_preference('receive_email')
    if current_user.type == UserType.STUDENT:
        clubs = current_user.clubs
        attendances = current_user.attendance

        # CAS calculation
        # add all attended activities
        cas = defaultdict(float)
        for attendance in attendances:
            cas[attendance.club] += attendance.cas
        # And all currently attending clubs
        for club in clubs:
            if club.is_active:
                cas[club]

        meetings_obj = current_user.activities_reminder(
            [ActivityTime.NOON, ActivityTime.AFTERSCHOOL])
        meetings = []
        meetings.extend([meeting for meeting in meetings_obj])
        acts_obj = current_user.activities_reminder([ActivityTime.UNKNOWN,
                                                     ActivityTime.HONGMEI,
                                                     ActivityTime.OTHERS])
        activities = []
        activities.extend([act for act in acts_obj])
        leader_club = filter(lambda club_obj: current_user == club_obj.leader,
                             clubs)
        return render_template('user/student.jinja2',
                               pictures=pictures,
                               clubs=clubs,
                               cas=cas,
                               meetings=meetings,
                               activities=activities,
                               leader_club=leader_club,
                               allow_club_creation=allow_club_creation,
                               receive_email=receive_email)
    else:
        years = (lambda m: map(lambda n: m + n, range(2)))(date.today().year)
        return render_template('user/admin.jinja2',
                               pictures=pictures,
                               years=years,
                               receive_email=receive_email)


@userblueprint.route('/submit_info', methods=['POST'])
@login_required
def personalsubmitinfo():
    '''Change user's information in database'''
    if request.form['name']:
        current_user.nickname = request.form['name']
    current_user.email = request.form['email']

    phone = request.form['phone']
    try:
        phone = int(phone)
    except ValueError:
        phone = None
    current_user.phone = phone
    if 'picture' in request.form:
        pic = int(request.form['picture'])
        if -pic in range(1, 21):
            current_user.picture = Upload(pic)
    if 'receive_email' in request.form:
        current_user.set_preference('receive_email', True)
    else:
        current_user.set_preference('receive_email', False)
    flash('Your information has been successfully changed.', 'status_info')
    return redirect(url_for('.personal'))


@userblueprint.route('/submit_password', methods=['POST'])
@login_required
def personalsubmitpassword():
    '''Change user's password in database'''
    user_login = User.attempt_login(current_user.studentid,
                                    request.form['old'])
    if user_login is None:
        fail('You have entered wrong old password. Please enter again.',
             'status_pw')
    elif request.form['new'] == '':
        fail('Please enter new password.', 'status_pw')
    elif request.form['new'] != request.form['again']:
        fail('You have entered two different passwords. '
             'Please enter again.', 'status_pw')
    else:
        try:
            current_user.password = request.form['new']
            flash('Your information has been successfully changed.',
                  'status_pw')
        except PasswordTooShort:
            fail('Password must be at least six digits.', 'status_pw')
    return redirect(url_for('.personal'))


@userblueprint.route('/info_download_all')
@special_access_required
@fresh_login_required
def allusersinfo():
    '''Allow admin to download all users' info'''
    info = []
    info.append(('ID', 'Class', 'Nick Name', 'Passport Name', 'Email',
                 'Phone'))
    info.extend([(user.id, user.grade_and_class, user.nickname,
                  user.passportname, user.email, str(user.phone))
                 for user in User.allusers()])

    return download_xlsx('All Users\' Info.xlsx', info)


@userblueprint.route('/refresh_users/submit', methods=['POST'])
@special_access_required
@fresh_login_required
def refreshusers_submit():
    '''Upload excel file to create new users'''
    from oclubs.worker import refresh_user
    refresh_user.delay()
    flash('Student accounts\' information has been successfully '
          'scheduled to refresh.', 'refresh_users')
    return redirect(url_for('.personal'))


@userblueprint.route('/rebuild_elastic_search/submit', methods=['POST'])
@special_access_required
@fresh_login_required
def rebuildsearch_submit():
    '''Rebuild elastic search engine to fix asyncronized situation'''
    from oclubs.worker import rebuild_elasticsearch
    rebuild_elasticsearch.delay()
    flash('Search engine has been scheduled to fix.', 'rebuild_search')
    return redirect(url_for('.personal'))


@userblueprint.route('/download_new_passwords')
@special_access_required
@fresh_login_required
def download_new_passwords():
    '''Allow admin to download new accounts' passwords'''
    result = []
    result.append(['Passport Name', 'Class', 'Password'])
    users = User.get_new_passwords()
    result.extend([(user.passportname,
                    user.grade_and_class,
                    password) for user, password in users])
    return download_xlsx('New Accounts\' Passwords.xlsx', result)


@userblueprint.route('/disable_accounts')
@special_access_required
@fresh_login_required
def disableaccounts():
    '''Allow admin to disable any account'''
    users = User.allusers()
    return render_template('user/disableaccounts.jinja2',
                           users=users)


@userblueprint.route('/disable_accounts/submit', methods=['POST'])
@special_access_required
@fresh_login_required
def disableaccounts_submit():
    '''Input disabling information into database'''
    user = User(request.form['id'])
    user.password = None
    flash(user.passportname + ' has been successfully disabled.',
          'disableaccounts')
    return redirect(url_for('.disableaccounts'))


@userblueprint.route('/change_password')
@special_access_required
@fresh_login_required
def changepassword():
    '''Allow admin to change users' password'''
    users = User.allusers(non_teachers=True)
    return render_template('user/changepassword.jinja2',
                           users=users)


@userblueprint.route('/change_password/submit', methods=['POST'])
@special_access_required
@fresh_login_required
def changepassword_submit():
    '''Input new password into database'''
    password = request.form['password']
    if password == '':
        fail('Please input valid password.', 'password')
        return redirect(url_for('.changepassword'))
    user = User(request.form['id'])
    try:
        user.password = password
    except PasswordTooShort:
        fail('Password must be at least six digits.', 'password')
        return redirect(url_for('.changepassword'))

    parameters = {'target_name': '%s (%s, %s)' % (
                      user.nickname,
                      user.passportname,
                      user.grade_and_class),
                  'performer_name': current_user.studentid}
    email.send(('clubsadmin@oclubs.shs.cn',), 'Admin changed password',
               render_email_template('adminchangepassword', parameters))
    flash(user.nickname + '\'s password has been successfully set to ' +
          password + '.', 'password')
    return redirect(url_for('.changepassword'))


@userblueprint.route('/forgot_password')
def forgotpw():
    '''Page for retrieving password'''
    return render_template('user/forgotpassword.jinja2')


@userblueprint.route('/change_info')
@special_access_required
@fresh_login_required
def changeuserinfo():
    '''Allow admin to change users' information'''
    users = User.allusers(non_teachers=True)
    return render_template('user/changeuserinfo.jinja2',
                           users=users)


@userblueprint.route('/change_info/submit', methods=['POST'])
@special_access_required
@fresh_login_required
def changeuserinfo_submit():
    '''Input change of info into database'''
    property_type = request.form['type']
    content = request.form['content'].strip()
    userid = request.form['userid']
    if content == '-':
        content = None
    else:
        try:
            content = int(content)
        except ValueError:
            pass

    try:
        setattr(User(userid), property_type, content)
    except Exception as e:
        status = type(e).__name__
    else:
        status = 'success'
    return jsonify({'result': status})


@userblueprint.route('/notifications/', defaults={'page': 1})
@userblueprint.route('/notifications/<int:page>')
@login_required
def notifications(page):
    '''Allow users to check their notifications'''
    note_num = 20
    notes_all = current_user.get_notifications(
        limit=((page-1)*note_num, note_num)
    )
    current_user.set_notifications_readall()
    invitations_all = current_user.get_invitation()
    num = current_user.get_unread_notifications_num()
    return render_template('user/notifications.jinja2',
                           notifications=notes_all[1],
                           number=num,
                           pagination=Pagination(page, note_num, notes_all[0]),
                           invitations=invitations_all)


@userblueprint.route('/notifications/submit', methods=['POST'])
@login_required
def invitation_reply():
    reply = request.form['reply']
    club = Club(request.form['club'])

    if not any(inv['club'] == club for inv in current_user.get_invitation()):
        abort(403)
    if reply == "accept":
        club.add_member(current_user)
        flash('You have successfully joined %s.' % club.name, 'reply')
    elif reply == "decline":
        flash('You have declined the invitation of %s.' % club.name, 'reply')
    current_user.delete_invitation(club)
    return redirect(url_for('.notifications'))


@userblueprint.route('/siteconfig')
@special_access_required
@fresh_login_required
def edit_siteconfig():
    types = {
        'allow_club_creation': {
            'name': 'Allow Student to Create Club Proposals',
            'desc': 'When this is allowed, students may propose clubs, '
                    'with themselves as leader, but they may not create '
                    'activities for the club before they are approved '
                    '(set to active). When this is not allowed, no one may '
                    'create new clubs.',
            'bool': ('Allowed', 'Not Allowed')
        },
        'enable_cleanup': {
            'name': 'Enable Auto-Cleanup',
            'desc': 'When this is enabled, an auto cleanup script will run '
                    'weekly to delete old activities, inactive clubs with no '
                    'activities left, disabled accounts without being a '
                    'leader of any club, etc. Allowing Club Creation implies '
                    'this disabled.',
            'bool': ('Enabled', 'Disabled')
        }
    }
    return render_template('user/siteconfig.jinja2',
                           siteconfig=siteconfig,
                           types=types)


@userblueprint.route('/siteconfig', methods=['POST'])
@special_access_required
@fresh_login_required
def edit_siteconfig_sumbit():
    '''Admin function: allow new club creation'''
    config_type = request.form['config_type']

    current = not siteconfig.get_config(config_type)
    siteconfig.set_config(config_type, current)

    # Check dependencies
    if siteconfig.get_config('allow_club_creation'):
        siteconfig.set_config('enable_cleanup', False)

    flash('Site configuration has been updated, please check the changes.',
          'siteconfig')
    return redirect(url_for('.edit_siteconfig'))


@userblueprint.route('/notify_all/submit', methods=['POST'])
@special_access_required
def notifyall_submit():
    '''Allow admin to notify all club leaders and members'''
    grade = request.form.get('grade', '')
    ntype = request.form.get('ntype', '')
    notify_contents = request.form['contents']
    if not notify_contents:
        flash('Please input something.', 'notify_all')
        return redirect(url_for('.personal'))

    if grade == '9-10':
        grade = ['9', '10']
    elif grade == '11-12':
        grade = ['11', '12']
    elif grade == 'all':
        grade = None
    else:
        flash('Invalid grade selection.', 'notify_all')
        return redirect(url_for('.personal'))

    notifylist = set()
    for club in Club.allclubs(grade_limit=grade):
        if ntype == 'leaderonly':
            notifylist.add(club.leader)
        elif ntype == 'all':
            notifylist.add(club.leader)
            notifylist.add(club.teacher)
            notifylist = notifylist.union(club.members)
        else:
            flash('Invalid grade selection.', 'notify_all')
            return redirect(url_for('.personal'))

    for user in notifylist:
        user.notify_user(notify_contents)
        parameters = {'user': user, 'notify_contents': notify_contents}
        contents = render_email_template('notifyall', parameters)
        user.email_user('Notification from admin', contents)
    flash('You have successfully notified them.', 'notify_all')
    return redirect(url_for('.personal'))
