---
name: auth-flask-login
description: >
  Use when the user asks about "Flask-Login", "Flask login and logout", "Flask user
  registration", "Flask authentication", "Flask login_required", "Flask password
  hashing", "Flask session auth", "protect Flask routes", "Flask logout POST CSRF",
  "Flask login next redirect", or needs the session-based login flow for a Flask 3
  application with CSRF protection.
---

# Flask Authentication with Flask-Login

## Overview

Session-based authentication for a Flask 3 app: Flask-Login keeps the signed-in user in the session cookie, Werkzeug hashes the passwords, and Flask-WTF `CSRFProtect` guards every form, including logout.

Building blocks:

- `LoginManager` created in `extensions.py`, bound with `login_manager.init_app(app)`, with `login_manager.login_view = 'auth.login'` for the redirect of anonymous users (all in `project-scaffold`).
- A `user_loader` callback in the factory that returns the user for the id in the session: `db.session.get(User, int(user_id))`.
- A `User` model that inherits `UserMixin` and stores only a password hash. The model itself is in `project-scaffold` (minimal) and in the `sqlalchemy-dev` plugin (`model-patterns`, `references/flask-login-user.md`).
- Routes `auth.login`, `auth.register`, `auth.logout` in one blueprint: `login_user(user)`, `logout_user()`, `@login_required` (below).
- `SECRET_KEY` set and kept stable: it signs the session. `CSRFProtect` initialised: `{{ csrf_token() }}` is undefined in a template without it.

Install with the SQLAlchemy pin (see `setup` for why):

```bash
pip install Flask Flask-Login Flask-WTF Flask-SQLAlchemy "SQLAlchemy<2.1"
```

## Routes

```python
# routes/auth.py
from urllib.parse import urlsplit

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db
from models import User

auth_bp = Blueprint('auth', __name__)

NAME_MAX, EMAIL_MAX = 100, 120   # String(100) and String(120) of the User columns
MIN_PASSWORD_LENGTH = 15    # NIST SP 800-63B-4: 15 when the password is the only factor, 8 with a second factor
MAX_PASSWORD_LENGTH = 128   # NIST asks for at least 64; a cap keeps one request from hashing megabytes

# Checked when the email is unknown, so "no such user" and "wrong password" cost the same time.
DUMMY_HASH = generate_password_hash('not-a-real-password', method='scrypt')


def local_target(target):
    """Return target only when it is a path on this site; None otherwise (open-redirect guard)."""
    if not target or not target.startswith('/') or target.startswith('//') or '\\' in target:
        return None
    parts = urlsplit(target)
    return None if parts.scheme or parts.netloc else target


def password_problem(password):
    """Length, not composition: NIST SP 800-63B-4 bans composition rules."""
    if len(password) < MIN_PASSWORD_LENGTH:
        return f'Password must be at least {MIN_PASSWORD_LENGTH} characters'
    if len(password) > MAX_PASSWORD_LENGTH:
        return f'Password must be at most {MAX_PASSWORD_LENGTH} characters'
    return None


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not name or not email:
            problem = 'Name and email are required'
        elif len(name) > NAME_MAX or len(email) > EMAIL_MAX:
            problem = f'Name must be at most {NAME_MAX} characters and email at most {EMAIL_MAX}'   # the column sizes: PostgreSQL raises instead of cutting
        else:
            problem = password_problem(password)
        if problem:
            flash(problem, 'error')
            return render_template('register.html')

        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password, method='scrypt'),
        )
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:     # the unique constraint on email decides, so two requests cannot both win
            db.session.rollback()
            flash('Email already registered', 'error')
            return render_template('register.html')
        login_user(user)
        flash('Registration successful!', 'success')
        return redirect(url_for('dashboard.dashboard'))
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = db.session.scalar(db.select(User).filter_by(email=email))
        password_ok = check_password_hash(user.password_hash if user else DUMMY_HASH, password)
        if user is not None and password_ok:
            login_user(user)
            return redirect(local_target(request.args.get('next')) or url_for('dashboard.dashboard'))
        flash('Wrong email or password', 'error')   # one message for both cases: no account enumeration
    return render_template('login.html')


@auth_bp.post('/logout')
@login_required
def logout():
    logout_user()
    flash('Signed out', 'success')
    return redirect(url_for('auth.login'))
```

Why it is written this way:

- **One error for login.** "You haven't registered yet" for an unknown email tells an attacker which addresses have accounts. Both failures give `Wrong email or password`, and the dummy hash keeps the response time the same.
- **Hash method named.** `generate_password_hash(password, method='scrypt')` is the Werkzeug 3 default; naming it fixes the choice in code. The hash is about 160 characters, so `String(256)` is enough. `check_password_hash` reads the method from the stored hash, so old hashes keep working when the method changes.
- **Registration on the constraint.** The `unique=True` column is the only check that survives two simultaneous sign-ups; the `IntegrityError` branch turns it into the same flash message. A register form still tells a visitor that an address is taken: if that matters, accept any address and confirm by e-mail.
- **`next` stays local.** `@login_required` redirects anonymous users to `/login?next=/path`; the login form posts back to the same URL, so `next` is still there. `local_target` rejects `https://evil.example`, `//evil.example` and `/\evil.example`.
- **Passwords: length, not composition.** NIST SP 800-63B-4 asks for at least 15 characters when the password is the only factor (8 with a second factor), at least 64 allowed, and no composition rules ("one digit and one special character" pushes people to `Password1!`). Check new passwords against a list of common and breached ones as well (a local list, or the k-anonymity range API of Have I Been Pwned); that is the rule that actually stops `correct-horse-1!`-style choices, and it needs no change to the routes except one more `elif` in `password_problem`.
- **Field sizes.** `name` and `email` are checked against the column sizes before the insert: SQLite stores an over-long value, PostgreSQL raises `DataError` and the visitor sees a 500.
- **Logout is `POST` with a CSRF token.** A `GET` logout is triggered by any other page (`<img src="/logout">`). The form is in `base.html` (`project-scaffold`).

## Rate limiting and "remember me"

- **Throttle `/login` and `/register`.** Nothing above limits guesses: every request costs the attacker one scrypt check at most. Flask-Limiter (`pip install Flask-Limiter`) adds a per-address limit, for example `@limiter.limit('5 per minute', methods=['POST'])` on both views, with a shared store (Redis) once you run more than one worker. Create the `Limiter` in `extensions.py` like the other extensions.
- **Sessions are not persistent here.** `login_user(user)` without `remember=True` signs the user in for the browser session only. If you add a "remember me" box (`login_user(user, remember=True)`), Flask-Login sets a second cookie that outlives the session; harden it like the session cookie: `REMEMBER_COOKIE_SECURE = True`, `REMEMBER_COOKIE_HTTPONLY = True`, `REMEMBER_COOKIE_SAMESITE = 'Lax'` in `ProductionConfig`, and a bounded `REMEMBER_COOKIE_DURATION` (the default is 365 days).

## Templates

```jinja2
{# templates/login.html #}
{% extends "base.html" %}
{% block title %}Log in{% endblock %}
{% block content %}
<h1>Log in</h1>
<form method="post">
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
  <label>Email <input type="email" name="email" required autofocus></label>
  <label>Password
    <span class="password-field">
      <input type="password" name="password" id="password" required>
      <button type="button" data-toggle-password="password">Show</button>
    </span>
  </label>
  <button type="submit">Log in</button>
</form>
<p><a href="{{ url_for('auth.register') }}">Create an account</a></p>
{% endblock %}
{% block scripts %}<script src="{{ url_for('static', filename='js/auth.js') }}" defer></script>{% endblock %}
```

The form has no `action`, so it posts to the URL it was loaded from and keeps `?next=`.

```jinja2
{# templates/register.html #}
{% extends "base.html" %}
{% block title %}Register{% endblock %}
{% block content %}
<h1>Create an account</h1>
<form method="post">
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
  <label>Name <input type="text" name="name" required autofocus maxlength="100"></label>
  <label>Email <input type="email" name="email" required maxlength="120"></label>
  <label>Password
    <span class="password-field">
      <input type="password" name="password" id="password" required minlength="15" maxlength="128">
      <button type="button" data-toggle-password="password">Show</button>
    </span>
  </label>
  <p class="hint">At least 15 characters. A passphrase of several words is fine; spaces and any characters are allowed.</p>
  <button type="submit">Register</button>
</form>
<p><a href="{{ url_for('auth.login') }}">I already have an account</a></p>
{% endblock %}
{% block scripts %}<script src="{{ url_for('static', filename='js/auth.js') }}" defer></script>{% endblock %}
```

Show / hide password:

```javascript
// static/js/auth.js
document.querySelectorAll('[data-toggle-password]').forEach(function (button) {
  button.addEventListener('click', function () {
    var input = document.getElementById(button.dataset.togglePassword);
    var show = input.type === 'password';
    input.type = show ? 'text' : 'password';
    button.textContent = show ? 'Hide' : 'Show';
  });
});
```

The navigation (`current_user.is_authenticated`: Log in / Register, or Dashboard / Log out) is in `templates/base.html` of `project-scaffold`.

## Protecting routes

```python
from flask_login import current_user, login_required

@clients_bp.route('/clients')
@login_required
def clients():
    # current_user is the signed-in User instance
    ...
```

- `@login_required` goes under `@route`. The login and register views stay public.
- To protect a whole app at once, use the `before_request` hook in `app-patterns` (Request Hooks) with a set of public endpoints.
- A route that serves JSON should answer `401`, not redirect to a login page: register `@login_manager.unauthorized_handler` for those blueprints.
- Every query for a signed-in user's rows is scoped to `current_user.id`, and a record fetched by an id from the URL is fetched together with its owner. Forgetting it exposes other users' data. The scoped helpers (`owned_by`, `one_or_404`) are in the `sqlalchemy-dev` plugin, `query-patterns`, `references/owner-scoped-queries.md`; the CRUD routes that use them are in `app-patterns`, `references/crud-views.md`.

## Tests

With `TestingConfig` (`WTF_CSRF_ENABLED = False`, see `app-patterns`, Testing):

```python
# tests/test_auth.py
import re

import pytest

from extensions import db
from models import User

PASSWORD = 'correct horse battery'   # 21 characters, no digit or symbol needed


def register(client, email='ann@example.com', password=PASSWORD, name='Ann'):
    return client.post('/register', data={'name': name, 'email': email, 'password': password})


def test_register_signs_in(client):
    response = register(client)
    assert response.status_code == 302
    assert client.get('/dashboard').status_code == 200


def test_each_client_has_its_own_user(app):
    ann, ben = app.test_client(), app.test_client()
    register(ann, 'ann@example.com', name='Ann')
    register(ben, 'ben@example.com', name='Ben')
    assert b'ann@example.com' in ann.get('/dashboard').data
    assert b'ben@example.com' in ben.get('/dashboard').data
    assert b'ann@example.com' not in ben.get('/dashboard').data


def test_password_rule_is_length(client):
    assert register(client, password='Short1!').status_code == 200            # 7 characters: refused
    assert b'at least 15' in register(client, password='Short1!').data
    assert register(client, password='x' * 129).status_code == 200            # over the cap: refused
    assert register(client).status_code == 302                                # a plain passphrase is accepted


def test_overlong_name_or_email_is_refused_before_the_insert(app, client):
    assert b'at most' in register(client, name='n' * 101).data
    assert b'at most' in register(client, email='e' * 110 + '@example.com').data
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count()).select_from(User)) == 0


def test_login_error_is_the_same_for_unknown_email_and_wrong_password(client):
    register(client)
    client.post('/logout')
    unknown = client.post('/login', data={'email': 'nobody@example.com', 'password': 'x'})
    wrong = client.post('/login', data={'email': 'ann@example.com', 'password': 'x'})
    assert b'Wrong email or password' in unknown.data
    assert b'Wrong email or password' in wrong.data


def test_logout_needs_post(client):
    register(client)
    assert client.get('/logout').status_code == 405
    assert client.post('/logout').status_code == 302
    assert client.get('/dashboard').status_code == 302


@pytest.mark.parametrize('target', ['https://evil.example/', '//evil.example/', '/\\evil.example/'])
def test_next_must_stay_on_the_site(client, target):
    register(client)
    client.post('/logout')
    response = client.post('/login?next=' + target,
                           data={'email': 'ann@example.com', 'password': PASSWORD})
    assert response.headers['Location'].endswith('/dashboard')


def test_password_is_stored_hashed(app, client):
    register(client)
    with app.app_context():
        user = db.session.scalar(db.select(User))
        assert user.password_hash != PASSWORD
        assert user.password_hash.startswith('scrypt:')


def test_login_form_needs_the_csrf_token(app, client):
    app.config['WTF_CSRF_ENABLED'] = True       # TestingConfig switches it off
    page = client.get('/login').data.decode()
    token = re.search(r'name="csrf_token" value="([^"]+)"', page).group(1)
    form = {'email': 'nobody@example.com', 'password': 'x'}
    assert client.post('/login', data=form).status_code == 400
    assert b'Wrong email or password' in client.post('/login', data={**form, 'csrf_token': token}).data
```

`test_each_client_has_its_own_user` depends on the fixture of `app-patterns`: it yields the app without an open app context, so each client's requests get their own `g` and their own Flask-Login user.

See `app-patterns` for the extension wiring, CSRF setup and error handlers, `jinja2-patterns` for template inheritance, `troubleshoot` for redirect loops and CSRF errors, and the `sqlalchemy-dev` plugin for the `User` model and queries.
