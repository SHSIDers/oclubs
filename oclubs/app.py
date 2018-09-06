# ! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals, division

import traceback
from urlparse import urlparse, urljoin

import random

from flask import (
    Flask, redirect, request, render_template, url_for, session, abort, flash,
    Markup,
)
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)
from htmlmin.minify import html_minify

from oclubs.objs import User, Club, Activity, FormattedText
from oclubs.access import done as db_done, email
from oclubs.access.secrets import get_secret
from oclubs.blueprints import actblueprint, clubblueprint, userblueprint, \
    resblueprint
from oclubs.enums import UserType, ClubType, ActivityTime, ClubJoinMode, \
    Building
from oclubs.exceptions import NoRow
from oclubs.redissession import RedisSessionInterface
from oclubs.shared import (
    encrypt, Pagination, render_email_template, form_is_valid, markdownexample,
    init_app, get_callsign_decorator, get_callsign
)
from oclubs.forms.miscellaneous_forms import LoginForm


app = Flask(__name__)

app.config['SECRET_KEY'] = get_secret('flask_key')

init_app(app)  # Must be before register_blueprint because of route()

app.register_blueprint(userblueprint, url_prefix='/user')
app.register_blueprint(clubblueprint, url_prefix='/club')
app.register_blueprint(actblueprint, url_prefix='/activity')
app.register_blueprint(resblueprint, url_prefix='/reservation')

app.session_interface = RedisSessionInterface()

app.jinja_env.globals['UserType'] = UserType
app.jinja_env.globals['ClubType'] = ClubType
app.jinja_env.globals['ActivityTime'] = ActivityTime
app.jinja_env.globals['ClubJoinMode'] = ClubJoinMode
app.jinja_env.globals['Building'] = Building

login_manager = LoginManager()
login_manager.init_app(app)


@app.before_request
def csrf_protect():
    if request.method == "POST":
        sessiontoken = session.get('_csrf_token', None)
        if not sessiontoken or request.form.get('_csrf_token') != sessiontoken:
            abort(418)


@app.after_request
def response_minify(response):
    if response.content_type.startswith('text/html'):
        response.set_data(
            html_minify(response.get_data(as_text=True))
        )

    return response


@app.after_request
def access_done(response):
    if response.status_code < 400 and form_is_valid():
        db_done(True)
    else:
        db_done(False)
    return response


@app.teardown_appcontext
def access_teardown(exception):
    db_done(False)


@app.errorhandler(404)
@app.route('/404')  # debugger
def page_not_found(e=None):
    '''Wrong url'''
    return render_template('static/error.html.j2',
                           error_type=404
                           ), 404


@app.errorhandler(403)
@app.route('/403')  # debugger
def forbidden(e=None):
    '''No access'''
    return render_template('static/error.html.j2',
                           error_type=403
                           ), 403


@app.errorhandler(401)
@app.route('/401')  # debugger
def unauthorized(e=None):
    '''Not logged in'''
    return render_template('static/error.html.j2',
                           error_type=401
                           ), 401


@app.errorhandler(500)
@app.route('/500')  # debugger
def internal_server_error(e=None):
    '''Internal server error'''
    flash(encrypt(traceback.format_exc()), '500')
    return render_template('static/error.html.j2',
                           error_type=500
                           ), 500


@app.errorhandler(418)
@app.route('/418')
def i_am_a_teapot(e=None):
    '''csrf violation'''
    return render_template('static/error.html.j2',
                           error_type=418
                           ), 418


@app.errorhandler(400)
@app.route('/400')
def bad_request(e=None):
    '''Incorrect url request'''
    return render_template('static/error.html.j2',
                           error_type=400,
                           ), 400


@login_manager.user_loader
def load_user(user_id):
    try:
        user = User(int(user_id))
        assert user.nickname and not user.is_disabled
        return user
    except Exception:
        return None


@login_manager.needs_refresh_handler
def refresh_login():
    '''Let user refresh its login status'''
    flash('Please login again for security.', 'login')
    return redirect(url_for('login', next=request.referrer
                            if request.method == 'POST' else request.path))


@app.route('/login', methods=['GET', 'POST'])
def login():
    '''Login page'''

    form = LoginForm()

    if request.method == "POST":
        if request.form['next'] != '':
            form.nexturl.process_data(request.form.get('next'))

        # first pass
        if form.is_firstPass.data == 'true':

            if form.check():

                userObj = User.get_userobj_from_passportname(
                    form.username.data)

                if userObj.initalized:
                    form.is_initalized.process_data('true')

                form.is_firstPass.process_data('false')

                return render_template('user/login.html.j2',
                                       form=form,
                                       is_firstPass=False,
                                       is_initalized=userObj.initalized)

            # form check failed
            else:
                return render_template('user/login.html.j2',
                                       form=form,
                                       is_firstPass=True,
                                       is_initalized=False)

        # second pass
        else:
            if form.check():
                # user initalization, create password, register email
                if form.is_initalized.data == 'false':
                    userObj = User.get_userobj_from_passportname(
                        form.username.data)

                    # to make sure the account is actually not initalized
                    # prevent using the initalization form to initalize an
                    # account that is actually already initalized
                    if userObj.initalized:
                        form.errors[form.username] = \
                            'This username has a password already.'
                        form.is_firstPass.process_data('true')
                        return render_template('user/login.html.j2',
                                               form=form,
                                               is_firstPass=True,
                                               is_initalized=False)

                    userObj.password = form.password.data
                    userObj.email = form.email.data
                    userObj.initalized = True

                    login_user(userObj)

                # regular user login
                else:
                    # if reset password request
                    if form.forgotpassword.data:
                        userObj = User.get_userobj_from_passportname(
                            form.username.data)
                        return redirect(
                            url_for('.reset_request', user=userObj.callsign))

                    userObj = User.attempt_login(
                        form.username.data,
                        form.password.data)

                    if userObj is not None:
                        login_user(userObj)

                        target = form.nexturl.data
                        if (not target or target == ''
                                or not is_safe_url(target)
                                or redirect_to_personal(target)):
                            return redirect(url_for('homepage'))
                        return redirect(target)
                    else:
                        form.errors[form.password] = \
                            'Incorrect username or password'

                        form.password.process_data('')

                        form.is_firstPass.process_data('true')

                        return render_template('user/login.html.j2',
                                               form=form,
                                               is_firstPass=True,
                                               is_initalized=False)

                # login success (no returns due to error)
                target = form.nexturl.data
                if (not target or target == ''
                        or not is_safe_url(target)
                        or redirect_to_personal(target)):
                    return redirect(url_for('homepage'))
                return redirect(target)

            # form check failed
            else:
                is_initalized = False
                if form.is_initalized.data == 'true':
                    is_initalized = True
                form.is_firstPass.process_data('true')
                return render_template('user/login.html.j2',
                                       form=form,
                                       is_firstPass=True,
                                       is_initalized=is_initalized)

    return render_template('user/login.html.j2',
                           form=form,
                           is_firstPass=True,
                           is_initalized=False)


@app.route('/requestreset/<user>', methods=['GET', 'POST'])
@get_callsign_decorator(User, 'user')
def reset_request(user):
    if request.method == 'POST':
        reset_request_id = User.new_reset_request(user)
        reset_link = url_for('.reset',
                             reset_request_id=reset_request_id,
                             _external=True)
        parameters = {'login_name': user.passportname,
                      'reset_link': reset_link}
        contents = render_email_template('reset', parameters)
        email.send((user.email, user.passportname),
                   'Reset Password - SHSID Connect',
                   contents)

        return render_template('user/request_reset.html.j2',
                               user=user,
                               is_sent=True)

    return render_template('user/request_reset.html.j2',
                           user=user,
                           is_sent=False)


@app.route('/reset/<reset_request_id>')
def reset(reset_request_id):
    form = LoginForm()

    user_callsign = User.get_reset_request(reset_request_id)

    if user_callsign != '':
        userObj = get_callsign(User, user_callsign)

        userObj.initalized = False
        form.is_firstPass.process_data('false')

        form.username.process_data(userObj.passportname)
        form.email.process_data(userObj.email)

        return render_template('user/login.html.j2',
                               form=form,
                               is_firstPass=False,
                               is_initalized=False)

    else:
        return render_template('user/request_reset.html.j2',
                               is_expired=True)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (test_url.scheme in ('http', 'https') and
            ref_url.netloc == test_url.netloc)


def redirect_to_personal(target):
    return target in map(url_for, ['login',
                                   'userblueprint.forgotpw',
                                   'homepage'])


@app.route('/logout')
def logout():
    '''Logout a user'''
    logout_user()
    return redirect(url_for('homepage'))


@app.route('/search')
def search():
    '''Search Page'''
    search_type = request.args.get('search_type', 'club')
    keywords = request.args.get('keywords', '')
    page = int(request.args.get('page', 1))

    if search_type == 'club':
        cls, title, desc, pic, extras = (
            Club, 'name', ['intro', 'description'], lambda obj: obj.picture,
            [])
    elif search_type == 'activity':
        cls, title, desc, pic, extras = (
            Activity, 'name', ['description', 'post'],
            lambda obj: obj.pictures[0] if obj.pictures else None,
            [('date', lambda obj: obj.date.isoformat())])

    search_result = cls.search(keywords, offset=(page-1)*10, size=10)

    results = []
    for result in search_result['results']:
        obj = result['object']
        highlight = result['highlight']

        try:
            resultdict = {
                'obj': obj,
                'name': _search_hl_or_attr(obj, highlight, [title]),
                'desc': _search_hl_or_attr(obj, highlight, desc),
                'pic': pic(obj)
            }
            for key, func in extras:
                resultdict[key] = func(obj)

            results.append(resultdict)
        except NoRow:  # database unsyncronized
            continue

    pagination = Pagination(page, 10, search_result['count'])

    return render_template('static/search.html.j2',
                           search_result=search_result,
                           results=results,
                           keywords=keywords,
                           search_type=search_type,
                           pagination=pagination)


def _search_hl_or_attr(obj, highlight, namelist):
    markup = []
    for name in namelist:
        if name in highlight:
            markup.extend(highlight[name])
        else:
            text = _search_gettext(obj, name)
            if text:
                markup.append(text)

    return Markup('... ').join(markup)


def _search_gettext(obj, name):
    obj = getattr(obj, name)

    try:
        obj = obj.raw
    except AttributeError:
        pass

    try:
        return obj[:256]
    except TypeError:
        return obj


homepage_slogans = (
    'Make New Friends.',
    'Uncover Your Passion.',
    'Start Clubbing!',
    'Work Together.',
    'Have Fun!',
    'Enhance Your Abilities.',
    'Discover Yourself.',
    'Really Fun!',
    'Accomplish Something.',
    'Create Something.',
)


@app.route('/')
def homepage():
    '''Homepage'''
    excellent_clubs = Club.excellentclubs()

    slogan = random.choice(homepage_slogans)

    info = {}
    for club in excellent_clubs:
        info[club.name] = club.activities()[0] \
            if club.activities() else None

    return render_template('static/homepage.html.j2',
                           is_home=True,
                           excellent_clubs=excellent_clubs,
                           info=info,
                           slogan=slogan)


@app.route('/about')
def about():
    '''About This Website'''
    return render_template('static/about.html.j2',
                           is_about=True)


@app.route('/feedback')
def feedback():
    '''Send feedback Page'''
    return render_template('static/feedback.html.j2')


@app.route('/feedback/submit', methods=['POST'])
def feedback_submit():
    '''Send feedback to us'''
    sender_name = request.form['name']
    sender_contact = request.form['contact']
    content = request.form['content']
    parameters = {'sender_name': sender_name,
                  'sender_contact': sender_contact,
                  'content': content}
    contents = render_email_template('feedback', parameters)
    email.send(('creators@oclubs.shs.cn',), 'Feedback', contents)
    email.send(('angleqian01@gmail.com',), 'Feedback', contents)
    flash('Your feedback has been sent to our team. Thank you for your time! Your feedback is invaluable.',
          'feedback')
    return redirect(url_for('.feedback'))


@app.route('/creators')
def creators():
    '''Introduction Page about Us'''
    return render_template('static/creators.html.j2')


@app.route('/reportbug')
def reportbug():
    '''Report bug'''
    return render_template('static/reportbug.html.j2')


@app.route('/reportbug/submit', methods=['POST'])
def reportbug_submit():
    '''Report bug'''
    content = request.form['content']
    content += ' ' + request.user_agent.string
    if current_user.is_authenticated:
        parameters = {'sender_name': '%s (%s, %s)' % (
                          current_user.nickname,
                          current_user.passportname,
                          current_user.grade_and_class),
                      'sender_contact': current_user.email + ' ' +
                      str(current_user.phone),
                      'content': content}
    else:
        parameters = {'sender_name': 'Anonymous',
                      'sender_contact': 'None',
                      'content': content}
    contents = render_email_template('contactadmin', parameters)
    email.send(('clubsadmin@oclubs.shs.cn',), 'Contact Admin', contents)
    email.send(('angleqian01@gmail.com',), 'Contact Admin', contents)
    flash('Your report has been sent to our team. Thank you for your time! We will fix the problem as soon as possible.',
          'reportbug')
    return redirect(url_for('.reportbug'))


@app.route('/markdown')
@login_required
def markdown():
    return render_template('static/markdown.html.j2',
                           raw=markdownexample,
                           rendered=Markup(FormattedText.format(
                               markdownexample)))


@app.route('/faq')
def faq():
    '''FAQ'''
    return render_template('static/faq.html.j2')


if __name__ == '__main__':
    app.run()
