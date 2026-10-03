---
name: troubleshoot
description: >
  Use when the user encounters "Flask errors", "Flask not working",
  "Flask import error", "Flask 500 error", "debug Flask", "Flask template not found",
  "Flask circular import", "FLASK_ENV ignored", "Flask CSRF token missing", or needs to diagnose and fix common Flask problems.
---

# Flask Troubleshooting

Diagnostic steps and fixes for common Flask problems.

## Quick Diagnostics

Run these checks first:

1. **App starts?** — `flask --app app run --debug` and check console output
2. **Routes registered?** — `flask routes` to list all endpoints
3. **Templates found?** — Verify `templates/` directory is sibling to app module
4. **Database accessible?** — Check `instance/` directory and SQLite file exists
5. **Dependencies installed?** — `pip list | grep Flask`

## Startup Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'flask'` | Flask not installed | `pip install Flask` |
| `Could not locate a Flask application` | Missing `--app` / `FLASK_APP` | Run `flask --app app run`, set `FLASK_APP=app` (or in `.flaskenv`), or ensure `app.py` exists |
| `FLASK_ENV=development` has no effect: debug mode and reloader stay off | `FLASK_ENV` was removed in Flask 2.3 and is ignored (so are `ENV` and `app.env`) | Use `flask run --debug` or `FLASK_DEBUG=1`; pick the config class with your own `APP_ENV` |
| `ImportError: cannot import name 'X' from 'models'` | Circular import | Move imports inside functions or use late imports |
| `Address already in use` (port 5000) | Port occupied | Use `--port 5001` or kill the other process |
| `OSError: [Errno 48] Address already in use` | macOS AirPlay on 5000 | Use port 5001: `flask run --port 5001` |

## Circular Import Errors

The most common Flask issue. Happens when `app.py` imports from `models.py` and `models.py` imports from `app.py`.

**Fix: Use the application factory pattern with late imports.**

```python
# extensions.py — NO import of app
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()  # Not bound to app yet

# models.py — imports extensions, never app
from extensions import db

# app.py
def create_app():
    app = Flask(__name__)
    from extensions import db  # Import INSIDE factory
    db.init_app(app)
    from routes.auth import auth_bp  # Import INSIDE factory
    app.register_blueprint(auth_bp)
    return app
```

## Template Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `TemplateNotFound: page.html` | Wrong template path | Ensure file is in `templates/` next to app module |
| `UndefinedError: 'variable' is undefined` | Variable not passed to template | Add variable to `render_template()` call |
| `UndefinedError: 'csrf_token' is undefined` | `csrf_token()` used but `CSRFProtect` is not initialised | `csrf = CSRFProtect()` in `extensions.py` and `csrf.init_app(app)` in the factory |
| `None` printed in the page by `{{ value\|default('N/A') }}` | `default` only replaces undefined values | Use `default('N/A', true)` to cover `None` and other falsy values |
| `TypeError: 'NoneType' is not iterable` | `None` passed to `{% for %}` | Use `{% for x in items or [] %}` or check before passing |
| Jinja2 syntax error | Wrong delimiter | Use `{{ }}` for expressions, `{% %}` for statements |

## Database Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `OperationalError: no such table` | Schema not created | Run `flask db upgrade` (Flask-Migrate); in tests call `db.create_all()` in the fixture |
| `OperationalError: table already exists` during `flask db upgrade` | Tables were first made by `db.create_all()` | Remove `create_all()` from the factory; for an existing schema that matches the models, `flask db stamp head` |
| `flask db migrate` prints "No changes in schema detected" on a new project and creates no revision | `db.create_all()` in the factory already created the tables | Remove it, delete the dev database, re-run `flask db migrate` and `flask db upgrade` |
| `DeprecationWarning: 'get_engine' is deprecated` from `migrations/env.py` (only visible with warnings enabled, e.g. `python -W error -m flask db migrate`) | The `env.py` template of Flask-Migrate 4.1 calls `db.get_engine()` first and falls back to `db.engine` | Harmless for now (the fallback covers Flask-SQLAlchemy 3.2); or change `get_engine()` in `env.py` to return `current_app.extensions['migrate'].db.engine` |
| `InvalidRequestError: Class ... is already a dataclass` | A `MappedAsDataclass` base on SQLAlchemy 2.1 with Flask-SQLAlchemy 3.1.x ([#1420](https://github.com/pallets-eco/flask-sqlalchemy/issues/1420); plain `db.Model` works) | `pip install "SQLAlchemy<2.1"` or drop `MappedAsDataclass` |
| `IntegrityError: UNIQUE constraint failed` | Duplicate value | Check for existing record before insert |
| `DetachedInstanceError` | Accessing object outside session | Access all needed attributes before session closes |
| `sqlite3.OperationalError: database is locked` | Concurrent writes | Use WAL mode or switch to PostgreSQL for production |

## Authentication Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `401 Unauthorized` / redirect loop | `@login_required` on login page | Exclude login route from auth checks |
| `AttributeError: 'AnonymousUserMixin'` | Accessing `current_user` when not logged in | Check `current_user.is_authenticated` first |
| Session lost on restart | No `SECRET_KEY` or changing key | Set a persistent `SECRET_KEY` via env var |
| Flash messages not showing | Missing template code | Add `get_flashed_messages()` block in base template |

## Form / Request Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `400 Bad Request` on form submit | Missing form field | Use `request.form.get('key')` instead of `request.form['key']` |
| `405 Method Not Allowed` | Route doesn't allow POST | Add `methods=['GET', 'POST']` to route decorator |
| `400 Bad Request: The CSRF token is missing.` | Form or AJAX call sends no token | Add `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">` (needs `CSRFProtect`), or send the `X-CSRFToken` header; the field name must equal `WTF_CSRF_FIELD_NAME` |
| `The CSRF session token is missing.` | No session cookie: `SECRET_KEY` changed, cookies blocked, or the page was cached across sessions | Set a stable `SECRET_KEY`; do not cache pages that contain forms |
| `The CSRF token has expired.` | Page open longer than `WTF_CSRF_TIME_LIMIT` (3600 s by default) or served from a cache | Reload the form; raise the limit or set it to `None` only if you accept the trade-off |
| `415 Unsupported Media Type` from `request.json` | Request has no `Content-Type: application/json` (a malformed body gives 400) | Send the header, or use `request.get_json(silent=True)` and handle `None` |
| File upload empty | Missing `enctype` | Add `enctype="multipart/form-data"` to form tag |

## Performance Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Slow page loads | N+1 queries | Use `selectinload()` for collections and `joinedload()` for many-to-one in SQLAlchemy queries (`subqueryload()` is a legacy strategy) |
| Memory growing | Debug mode in production | Set `FLASK_DEBUG=0` in production |
| Static files slow | No caching headers | Configure web server (Nginx) for static file serving |

## Debug Mode

Enable detailed error pages and auto-reload during development:

```bash
flask --app app run --debug
```

**Never enable debug mode in production** — it exposes an interactive debugger that allows arbitrary code execution.

## Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
app.logger.info('Processing request for %s', request.path)
app.logger.error('Failed to save: %s', str(e))
```
