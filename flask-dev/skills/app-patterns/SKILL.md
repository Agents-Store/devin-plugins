---
name: app-patterns
description: >
  Use when the user asks about "Flask application factory", "Flask blueprints",
  "Flask config management", "Flask extensions", "organize Flask project",
  "Flask app structure", "register Flask blueprint", "Flask context processors",
  "Flask CSRFProtect", "Flask production config", "test a Flask app",
  "Flask CRUD routes", "Flask list/edit/delete views", "Flask form to database",
  or needs patterns for structuring a Flask application.
---

# Flask Application Patterns

Production-tested patterns for Flask application structure, configuration, and extension management.

The examples use a flat layout: `app.py` (factory), `config.py`, `extensions.py`, `models.py`, `routes/`, `templates/`. The example application is called `myapp`.

## Application Factory

Always use the factory pattern. It enables testing, multiple instances, and avoids circular imports.

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

Do not call `db.create_all()` in the factory. With Flask-Migrate the tables then already exist, so `flask db migrate` reports "No changes in schema detected" and creates no revision, and a fresh database never gets a migration that builds the schema. Create the schema with `flask db upgrade`; `db.create_all()` belongs only in test fixtures (see Testing).

## Blueprint Organization

Each blueprint is a self-contained module with its own routes, templates, and static files.

### Basic Blueprint

```python
# routes/clients.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Client

clients_bp = Blueprint('clients', __name__)

@clients_bp.route('/clients')
@login_required
def clients():
    clients_list = db.session.scalars(
        db.select(Client).filter_by(user_id=current_user.id)
    ).all()
    return render_template('clients.html', clients=clients_list)

@clients_bp.route('/clients/add', methods=['POST'])
@login_required
def add_client():
    client = Client(
        user_id=current_user.id,
        name=request.form['name'],
        phone=request.form['phone'],
    )
    db.session.add(client)
    db.session.commit()
    flash('Client added successfully', 'success')
    return redirect(url_for('clients.clients'))
```

Use `db.session.execute(db.select(...))` / `db.session.scalars(...)`. `Model.query` is the legacy interface; see the `sqlalchemy-dev` plugin for model and query patterns.

### Blueprint with URL Prefix

```python
# For API-style routes
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# All routes under /api/v1/
@api_bp.route('/clients')
def list_clients():
    ...
```

### Blueprint Registration Order

Register blueprints in the factory. Order matters only when URL rules overlap:

```python
# In create_app()
app.register_blueprint(auth_bp)        # /login, /register, /logout
app.register_blueprint(dashboard_bp)   # /dashboard
app.register_blueprint(clients_bp)     # /clients
app.register_blueprint(api_bp)         # /api/v1/*
```

### CRUD Views

List, create, edit and delete routes with their templates and forms, a dashboard with aggregates, and a select box fed from a related table, all scoped to the signed-in user, are in [CRUD views](references/crud-views.md). The scoped queries they call (`owned_by()`) are in the `sqlalchemy-dev` plugin, `query-patterns`, `references/owner-scoped-queries.md`. The rules in short: every view is `@login_required` and starts from `owned_by(Model, current_user.id)`; every `POST` form carries `csrf_token`; a successful `POST` commits once and redirects; delete is a `POST`.

## Configuration Management

### Environment-Based Config

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

### Choosing the config and debug mode

`FLASK_ENV` was removed in Flask 2.3 together with the `ENV` config key and the `app.env` attribute, so `FLASK_ENV=development` in `.flaskenv` or the shell is silently ignored on Flask 3. Use your own variable (`APP_ENV`) to pick the config class, and control debug mode only through `--debug` or `FLASK_DEBUG`:

```bash
# .flaskenv  (committed: public values only; needs python-dotenv)
FLASK_APP=app
APP_ENV=development
FLASK_DEBUG=1
```

```bash
# .env  (gitignored: private values)
SECRET_KEY=<output of: python -c "import secrets; print(secrets.token_hex(32))">
```

Do not set `DEBUG = True` in a config class. The `flask` command re-sets `app.debug` from `--debug` / `FLASK_DEBUG` after the app loads, so a config value without the flag is overwritten (`DEBUG = True` in config and no `--debug` gives `app.debug == False`), and the Flask docs discourage it.

### Production settings (Flask 3.1+)

| Setting | Default | Purpose |
|---------|---------|---------|
| `SECRET_KEY_FALLBACKS` | `None` | Old keys still accepted for unsigning, for key rotation without logging everyone out. Flask's own session honours it; extensions that sign with `SECRET_KEY` themselves may not |
| `TRUSTED_HOSTS` | `None` | Allow-list for the `Host` header; a mismatch returns 400. A leading dot matches subdomains |
| `MAX_FORM_MEMORY_SIZE` | `500_000` | Max bytes of one non-file field in a `multipart/form-data` body; over the limit returns 413 |
| `MAX_FORM_PARTS` | `1_000` | Max fields in a `multipart/form-data` body; over the limit returns 413 |
| `SESSION_COOKIE_PARTITIONED` | `False` | `Partitioned` (CHIPS) cookie attribute for embedded/iframe use; implies `SESSION_COOKIE_SECURE` |

```python
# config.py: ProductionConfig with the Flask 3.1 settings added
class ProductionConfig(Config):
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    TRUSTED_HOSTS = ['myapp.example.com']
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    SECRET_KEY_FALLBACKS = [
        k for k in os.environ.get('SECRET_KEY_FALLBACKS', '').split(',') if k
    ]
```

## Extension Initialization

Create extensions in `extensions.py` (no import of the app), then bind them in `create_app()` with `init_app`. `Base` is the SQLAlchemy 2.0 declarative base: it makes `db.Model` accept `Mapped[...]` annotations, and its naming convention gives constraints and indexes stable names for Alembic:

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

Install with the SQLAlchemy pin (a `MappedAsDataclass` base fails on SQLAlchemy 2.1, issue #1420; plain `db.Model` works, but pin to be safe; see the `setup` skill):

```bash
pip install Flask Flask-SQLAlchemy "SQLAlchemy<2.1" Flask-Migrate Flask-Login Flask-WTF
```

### CSRF protection

`CSRFProtect` checks the token on every `POST`/`PUT`/`PATCH`/`DELETE` request. Without `csrf.init_app(app)`, `{{ csrf_token() }}` in a template raises `UndefinedError: 'csrf_token' is undefined`. Forms built with `FlaskForm` get a token through `{{ form.hidden_tag() }}` or `{{ form.csrf_token }}`; plain HTML forms render it by hand:

```jinja2
<form method="post">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
</form>
```

For JavaScript clients render the token once and send it in the `X-CSRFToken` header:

```jinja2
<head>{{ csrf_meta_tag() }}</head>   {# Flask-WTF 1.3+: <meta name="csrf-token" content="..."> #}
```

Before Flask-WTF 1.3 write the tag by hand: `<meta name="csrf-token" content="{{ csrf_token() }}">`.

Return a friendly page for a failed check, and exempt only what must be exempt (webhooks, token-authenticated APIs):

```python
# app.py: import at the top of the file
from flask_wtf.csrf import CSRFError

# inside create_app()
@app.errorhandler(CSRFError)
def csrf_error(e):
    return render_template('errors/400.html', reason=e.description), 400

csrf.exempt(webhook_bp)   # a whole blueprint; or @csrf.exempt on one view
```

## Context Processors

Add variables available in all templates:

```python
# app.py: import at the top of the file
from datetime import datetime

# inside create_app()
@app.context_processor
def inject_globals():
    return {
        'now': datetime.now(),
        'app_name': 'myapp',
    }
```

## Error Handlers

Register custom error pages:

```python
# app.py: import at the top of the file
from flask import render_template

# inside create_app()
@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500
```

## Request Hooks

```python
# app.py: imports at the top of the file
from flask import redirect, request, url_for
from flask_login import current_user

# inside create_app()
@app.before_request
def require_login():
    """Redirect unauthenticated users to login for protected pages."""
    public_endpoints = {'auth.login', 'auth.register', 'static'}
    if request.endpoint is None:
        return None   # no route matched (404, rejected Host): let Flask answer
    if request.endpoint not in public_endpoints and not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response
```

Keep the `endpoint is None` guard: when routing fails (unknown URL, or a Host rejected by `TRUSTED_HOSTS`) there is no URL adapter, so `url_for()` in the hook would raise and turn a 404 or 400 into a 500.

## Testing

Build the app with `create_app(TestingConfig)`. This is the one place for `db.create_all()`:

```python
# tests/conftest.py
import pytest

from app import create_app
from config import TestingConfig
from extensions import db


@pytest.fixture()
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()   # tests only; real schema comes from `flask db upgrade`
    yield app             # no app context stays open during the test
    with app.app_context():
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
```

```python
# tests/test_app.py
def test_login_page(client):
    assert client.get('/login').status_code == 200

def test_dashboard_requires_login(client):
    response = client.get('/dashboard')
    assert response.status_code == 302            # 303 on Flask 3.2+, see below
    assert '/login' in response.headers['Location']

def test_seed_command(runner):
    result = runner.invoke(args=['seed'])
    assert 'Database seeded.' in result.output
```

The fixture yields the app **outside** an app context, on purpose. Every `client.get()` then gets its own app context, like a real request: its own `db.session` (closed and rolled back at the end of the request), its own `g`, and its own Flask-Login user. Holding one context open for the whole test (`yield app` inside the `with` block) makes all requests share one session and one cached `current_user`: a view that forgets `commit()` still passes (the next request sees the pending row), and a second client looks signed in as the first user. A test that reads the database itself opens a context for it:

```python
# tests/test_register.py
from extensions import db
from models import User


def test_registered_user_is_stored(app, client):
    client.post('/register', data={'name': 'Ann', 'email': 'ann@example.com', 'password': 'correct horse battery'})
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count()).select_from(User)) == 1   # only what was committed
```

`db.session` outside a request or a `with app.app_context():` block raises `RuntimeError: Working outside of application context`.

`WTF_CSRF_ENABLED = False` in `TestingConfig` lets tests post forms without a token. Keep one test with CSRF enabled for the login form if the token matters.

## Upgrade watch list: Flask 3.2

Flask 3.2 is unreleased (development on `main` as of 2026-10). Announced changes that touch application code:

| Change | What to do |
|--------|-----------|
| Python 3.9 dropped (3.10+) | Set the project floor to 3.10 now |
| `redirect()` returns 303 instead of 302 | Tests that assert `302` should accept the new code or check `Location` only |
| `RequestContext` merged into `AppContext` (old name stays as deprecated alias) | Matters for code and extensions that import `RequestContext` |
| `template_filter` / `template_test` / `template_global` usable without parentheses | Optional |
| All teardown callbacks run even if one raises; `should_ignore_error` deprecated | Handle errors inside teardown handlers |
| New `app.query` route decorator (HTTP `QUERY`) | Optional |
