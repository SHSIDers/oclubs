#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals, division


import traceback
from uuid import uuid4
from urlparse import urlparse, urljoin

from flask import (
    Flask, redirect, request, render_template, url_for, session, abort, flash,
    Markup, Response
)
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)
from htmlmin.minify import html_minify

from oclubs.objs import User, Club, Activity, Upload
from oclubs.access import done as db_done, get_secret, email
from oclubs.blueprints import actblueprint, clubblueprint, userblueprint
from oclubs.enums import UserType, ClubType, ActivityTime, ClubJoinMode
from oclubs.exceptions import NoRow
from oclubs.redissession import RedisSessionInterface
from oclubs.shared import (
    encrypt, Pagination, render_email_template, form_is_valid
)


app = Flask(__name__)

app.config['SECRET_KEY'] = get_secret('flask_key')

app.register_blueprint(userblueprint, url_prefix='/user')
app.register_blueprint(clubblueprint, url_prefix='/club')
app.register_blueprint(actblueprint, url_prefix='/activity')

app.session_interface = RedisSessionInterface()

app.jinja_env.globals['UserType'] = UserType
app.jinja_env.globals['ClubType'] = ClubType
app.jinja_env.globals['ActivityTime'] = ActivityTime
app.jinja_env.globals['ClubJoinMode'] = ClubJoinMode


login_manager = LoginManager()
login_manager.init_app(app)


def get_picture(picture, ext='jpg'):
    return url_for('static', filename='images/' + picture + '.' + ext)

app.jinja_env.globals['getpicture'] = get_picture


def url_for_other_page(page):
    args = request.view_args.copy()
    args.update(request.args)
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page


@app.before_request
def csrf_protect():
    if request.method == "POST":
        sessiontoken = session.get('_csrf_token', None)
        if not sessiontoken or request.form.get('_csrf_token') != sessiontoken:
            abort(418)


def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = str(uuid4())
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token


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
    return render_template('static/error.html',
                           error_type=404
                           ), 404


@app.errorhandler(403)
@app.route('/403')  # debugger
def forbidden(e=None):
    '''No access'''
    return render_template('static/error.html',
                           error_type=403
                           ), 403


@app.errorhandler(401)
@app.route('/401')  # debugger
def unauthorized(e=None):
    '''Not logged in'''
    return render_template('static/error.html',
                           error_type=401
                           ), 401


@app.errorhandler(500)
@app.route('/500')  # debugger
def internal_server_error(e=None):
    '''Internal server error'''
    flash(encrypt(traceback.format_exc()), '500')
    return render_template('static/error.html',
                           error_type=500
                           ), 500


@app.errorhandler(418)
@app.route('/418')
def i_am_a_teapot(e=None):
    '''csrf violation'''
    return render_template('static/error.html',
                           error_type=418
                           ), 418


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


@app.route('/login')
def login():
    '''Login page'''
    return render_template('user/login.html')


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (test_url.scheme in ('http', 'https') and
            ref_url.netloc == test_url.netloc)


def redirect_to_personal(target):
    return target in map(url_for, ['login', 'userblueprint.forgotpw','homepage'])


@app.route('/login/submit', methods=['POST'])
def login_submit():
    '''API to login'''
    user = User.attempt_login(
        request.form['username'],
        request.form['password']
    )
    if user is not None:
        # Just in case a teacher somehow got a valid password...
        if user.type == UserType.TEACHER:
            flash('Teachers may not login.', 'login')
            return redirect(url_for('login'))

        login_user(user, remember=('remember' in request.form))

        target = request.form.get('next')
        if not target or not is_safe_url(target) or redirect_to_personal(target):
            return redirect(url_for('userblueprint.personal'))
        return redirect(target)
    else:
        flash('Please enter your username and password correctly '
              'in order to login.', 'login')
        return redirect(url_for('login'))


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
    else:
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

    return render_template('static/search.html',
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


@app.route('/')
def homepage():
    '''Homepage'''
    top_pic = []
    sizes = [3, 6, 3, 6, 3, 3]
    acts = Activity.get_activities_conditions(
        require_photos=True, limit=len(sizes))[1]

    top_pic.extend([{
        'picture': act.pictures[0],
        'actname': act.name,
        'content': act.description.formatted,
        'link': url_for('actblueprint.actintro', activity=act.callsign)
    } for act in acts])

    top_pic.extend([{
        'picture': Upload(-101),
        'actname': 'Default',
        'content': 'Oops, we don\'t have much picture',
        'link': '#'
    } for _ in range(len(sizes) - len(top_pic))])

    for num, (pic, size) in enumerate(zip(top_pic, sizes)):
        pic['id'] = 'img' + str(num)
        pic['size'] = size

    blockpiccss = url_for('gen_blockpic_css', **{pic['id']: pic['picture'].id
                                                 for pic in top_pic})

    ex_clubs = Club.excellentclubs(3)
    pic_acts = top_pic[0:3]
    return render_template('static/homepage.html',
                           is_home=True,
                           top_pic=top_pic,
                           blockpiccss=blockpiccss,
                           ex_clubs=ex_clubs,
                           pic_acts=pic_acts)


@app.route('/blockpic.css')
def gen_blockpic_css():
    css = "#blockpic-img%d{background-image:url(%s)}"
    ret = ''
    for key, value in request.args.iteritems():
        if key.startswith('img'):
            ret += css % (int(key[3:]), Upload(int(value)).location_external)

    return Response(ret, mimetype='text/css')


@app.route('/about')
def about():
    '''About This Website'''
    return render_template('static/about.html',
                           is_about=True)


@app.route('/contact_creators')
def contactcreators():
    '''Advice Page'''
    return render_template('static/contactcreators.html')


@app.route('/contact_creators/submit', methods=['POST'])
def contactcreators_submit():
    '''Send advice to us'''
    sender_name = request.form['name']
    sender_contact = request.form['contact']
    content = request.form['content']
    parameters = {'sender_name': sender_name,
                  'sender_contact': sender_contact,
                  'content': content}
    contents = render_email_template('contactcreators', parameters)
    email.send(('creators@oclubs.shs.cn',), 'Contact Creators', contents)
    flash('The information has been successfully sent to creators.',
          'contact_creators')
    return redirect(url_for('.contactcreators'))


@app.route('/creators')
def creators():
    '''Introduction Page about Us'''
    return render_template('static/creators.html')


@app.route('/contact_admin')
@login_required
def contactadmin():
    '''Complaints Page'''
    return render_template('static/contactadmin.html')


@app.route('/contact_admin/submit', methods=['POST'])
@login_required
def contactadmin_submit():
    '''Submit complaints'''
    content = request.form['content']
    parameters = {'sender_name': current_user.nickname + ' (' +
                  current_user.passportname + ')',
                  'sender_contact': current_user.email + ' ' +
                  str(current_user.phone),
                  'content': content}
    contents = render_email_template('contactadmin', parameters)
    email.send(('clubsadmin@oclubs.shs.cn',), 'Contact Admin', contents)
    flash('The information has been successfully sent to adminstrators.',
          'contact_admin')
    return redirect(url_for('.contactadmin'))


if __name__ == '__main__':
    app.run()
