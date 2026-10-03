---
name: project-scaffold
description: >
  Use when the user asks to "create a new Flask project", "scaffold a Flask app",
  "start a Flask project", "Flask project structure", "Flask project layout",
  "init Flask project", "Flask with SQLAlchemy and migrations from scratch", or needs
  the initial layout, application factory, config, .env and .gitignore for a new
  Flask 3 application.
---

# Flask Project Scaffold

## Overview

A new Flask 3 project that starts, logs a user in and migrates its database on the first run: the application factory, config classes chosen by an `APP_ENV` variable, extensions in `extensions.py` (Flask-SQLAlchemy, Flask-Migrate, Flask-Login, `CSRFProtect`), a `User` model, a dashboard blueprint, a base template, and the `.flaskenv` / `.env` / `.gitignore` files. The files are complete: create them as written, in order, and `flask db upgrade` builds the `users` table from a migration revision.

The login, registration and logout routes and their templates are in `auth-flask-login`; the factory below already registers that blueprint (step 7).

Layout (flat, application name `myapp`):

```
myapp/
├── app.py              # create_app() factory
├── config.py           # Development / Production / Testing config classes
├── extensions.py       # Base, db, migrate, login_manager, csrf (no app imported)
├── models.py           # SQLAlchemy models
├── routes/
│   ├── __init__.py
│   ├── auth.py         # login, register, logout (auth-flask-login)
│   └── dashboard.py    # landing page
├── templates/          # base.html, dashboard.html, login.html, register.html
├── static/
│   ├── css/base.css
│   └── js/auth.js      # password show/hide (auth-flask-login)
├── tests/              # conftest.py and tests (app-patterns, Testing)
├── migrations/         # created by flask db init, committed
├── instance/           # SQLite database in development (gitignored)
├── pytest.ini
├── requirements.txt
├── .flaskenv           # FLASK_APP, APP_ENV, FLASK_DEBUG (public, committed)
├── .env                # SECRET_KEY, DATABASE_URL (private, gitignored)
└── .gitignore
```

## 1. Python and install

Python 3.10 or newer. Flask-SQLAlchemy 3.1.1 (the latest release) declares `sqlalchemy>=2.0.16` with no upper bound, so a plain install pulls SQLAlchemy 2.1. A `MappedAsDataclass` base fails on SQLAlchemy 2.1 ([pallets-eco/flask-sqlalchemy#1420](https://github.com/pallets-eco/flask-sqlalchemy/issues/1420); plain `db.Model` works), so pin `SQLAlchemy<2.1` to be safe until Flask-SQLAlchemy supports 2.1, in `requirements.txt` as well as on the command line:

```
# requirements.txt
Flask>=3.1
Flask-SQLAlchemy>=3.1.1
SQLAlchemy>=2.0.16,<2.1
Flask-Migrate>=4.1
Flask-Login>=0.6.3
Flask-WTF>=1.2
python-dotenv>=1.0
```

```bash
# from the project root
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
```

## 2. Environment files

```
# .flaskenv
FLASK_APP=app
APP_ENV=development
FLASK_DEBUG=1
```

```
# .gitignore
.env
instance/
.venv/
__pycache__/
*.pyc
.claude/settings.local.json
```

`.env` is private. Generate the secret instead of typing one:

```bash
printf 'SECRET_KEY=%s\n' "$(python3 -c 'import secrets; print(secrets.token_hex(32))')" > .env
```

Production adds `DATABASE_URL` (the development config falls back to `sqlite:///dev.db`, stored in `instance/`).

The `flask` command loads `.flaskenv` and `.env` itself (python-dotenv), and real environment variables win over both files. gunicorn and other WSGI servers do not read them: a production deployment sets `APP_ENV=production`, `SECRET_KEY` and `DATABASE_URL` in the real environment, and does not ship the development `.flaskenv` values.

## 3. Config classes

```python
# config.py
import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')   # create_app() refuses to start without it
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')


class ProductionConfig(Config):
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = 'testing'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False   # TESTING alone does not switch CSRF off


CONFIGS = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}
```

There is no `DEBUG` here: debug mode comes from `--debug` / `FLASK_DEBUG`. More settings (Flask 3.1 production keys, `SECRET_KEY_FALLBACKS`): `app-patterns`.

## 4. Extensions

`Base` carries a naming convention, so constraints and indexes get stable names that Alembic autogenerate and SQLite batch migrations rely on (details in the `sqlalchemy-dev` plugin, `model-patterns`).

```python
# extensions.py
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


db = SQLAlchemy(model_class=Base)
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please sign in first'
csrf = CSRFProtect()
```

## 5. Models

```python
# models.py
import datetime as dt

from flask_login import UserMixin
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from extensions import db


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
```

`Mapped[str]` is `NOT NULL`; `Mapped[str | None]` is nullable. The `sqlalchemy-dev` plugin (`model-patterns`, with `references/flask-login-user.md`) covers the `User` model in depth and every other model.

## 6. Application factory

```python
# app.py
import os
from flask import Flask

from config import CONFIGS
from extensions import csrf, db, login_manager, migrate


def create_app(config_class=None):
    app = Flask(__name__)

    # Explicit class (tests) wins; otherwise our own APP_ENV picks it.
    # FLASK_ENV is ignored: removed in Flask 2.3. Use our own APP_ENV.
    app.config.from_object(config_class or CONFIGS[os.environ.get('APP_ENV', 'production')])
    if not app.config.get('SECRET_KEY'):
        raise RuntimeError('SECRET_KEY is not set')

    # Bind extensions (created in extensions.py)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    return app
```

`from models import User` inside the factory puts every model on `db.metadata` before Flask-Migrate reads it, and avoids a circular import. Import each new model module there (or in `models.py`) too: a model that nothing imports is invisible to `flask db migrate`.

## 7. Blueprints

```python
# routes/__init__.py
```

```python
# routes/dashboard.py
from flask import Blueprint, render_template
from flask_login import login_required

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')
```

Create `routes/auth.py`, `templates/login.html`, `templates/register.html` and `static/js/auth.js` from `auth-flask-login`. Add each new feature as one more blueprint file registered in the factory.

## 8. Templates and static files

The logout control is a `POST` form with a CSRF token, not a link: a link would let any other site sign users out.

```jinja2
{# templates/base.html #}
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}myapp{% endblock %}</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/base.css') }}">
  {% block extra_css %}{% endblock %}
</head>
<body>
  <nav>
    {% if current_user.is_authenticated %}
      <a href="{{ url_for('dashboard.dashboard') }}">Dashboard</a>
      <form method="post" action="{{ url_for('auth.logout') }}" class="inline">
        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
        <button type="submit">Log out ({{ current_user.name }})</button>
      </form>
    {% else %}
      <a href="{{ url_for('auth.login') }}">Log in</a>
      <a href="{{ url_for('auth.register') }}">Register</a>
    {% endif %}
  </nav>

  {% with messages = get_flashed_messages(with_categories=true) %}
    {% for category, message in messages %}
      <div class="flash flash-{{ category }}">{{ message }}</div>
    {% endfor %}
  {% endwith %}

  <main>{% block content %}{% endblock %}</main>
  {% block scripts %}{% endblock %}
</body>
</html>
```

```jinja2
{# templates/dashboard.html #}
{% extends "base.html" %}
{% block title %}Dashboard{% endblock %}
{% block content %}
<h1>Dashboard</h1>
<p>Signed in as {{ current_user.email }}.</p>
{% endblock %}
```

```css
/* static/css/base.css */
form.inline { display: inline; }
.flash-error { color: #b00020; }
.flash-success { color: #1b5e20; }
```

## 9. First migration and run

```bash
# run from the project root, after the files above exist and .env holds SECRET_KEY
flask db init
flask db migrate -m "Initial schema"
grep -n "create_table" migrations/versions/*.py   # must show 'users': read the revision before applying it
flask db upgrade
flask routes
flask run
```

Open `http://127.0.0.1:5000/register`, create an account, sign out, sign in again. Where port 5000 is taken (macOS AirPlay Receiver), run `flask run --port 5001`.

After `flask db migrate`, a revision with no `create_table('users'` means that the model was not imported (step 6) or that the tables already exist in the database (a `create_all()` call somewhere). Fix that before `flask db upgrade`.

`flask db init` writes a `migrations/env.py` whose `get_engine()` helper calls a Flask-SQLAlchemy API that 3.1 deprecates; it surfaces only as a `DeprecationWarning` when warnings are errors, and the `sqlalchemy-dev` plugin's `cli-recipes` has the two-line fix.

## 10. Tests

`pytest.ini` puts the project root on the import path (so `tests/conftest.py` can `from app import create_app`) and turns SQLAlchemy's deprecation warnings, `LegacyAPIWarning` included, into errors, so a legacy call fails a test instead of passing silently:

```ini
# pytest.ini
[pytest]
pythonpath = .
testpaths = tests
filterwarnings =
    error::sqlalchemy.exc.SADeprecationWarning
```

```bash
pip install pytest
pytest
```

`tests/conftest.py` (the `app`, `client` and `runner` fixtures) and the first tests are in `app-patterns`, Testing; the login-flow tests are in `auth-flask-login`.

## Rules the scaffold follows

- No `db.create_all()` in the factory; the schema comes from `flask db upgrade` (`create_all()` only in test fixtures).
- `SECRET_KEY` has no fallback value: the factory raises when it is missing.
- Debug mode comes from `--debug` / `FLASK_DEBUG`, never from a config class.
- Queries use `db.session.execute(db.select(...))`, not `Model.query`.
- `SQLALCHEMY_TRACK_MODIFICATIONS` is not set: `False` is the default.
- Logout is `POST` with a CSRF token.

See `app-patterns` for blueprints, CSRF, context processors, request hooks, testing and CRUD views; `auth-flask-login` for the login flow; `setup` to check an existing project; `cli-recipes` for `flask` commands; the `sqlalchemy-dev` plugin for models, queries and migrations.
