---
name: troubleshoot
description: >
  Use when the user encounters "Flask errors", "Flask not working",
  "Flask import error", "Flask 500 error", "debug Flask", "Flask template not found",
  "Flask circular import", or needs to diagnose and fix common Flask problems.
---

# Flask Troubleshooting

Diagnostic steps and fixes for common Flask problems.

## Quick Diagnostics

Run these checks first:

1. **App starts?** — `flask run --debug` and check console output
2. **Routes registered?** — `flask routes` to list all endpoints
3. **Templates found?** — Verify `templates/` directory is sibling to app module
4. **Database accessible?** — Check `instance/` directory and SQLite file exists
5. **Dependencies installed?** — `pip list | grep Flask`

## Startup Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'flask'` | Flask not installed | `pip install Flask` |
| `Could not locate a Flask application` | Missing `FLASK_APP` | Set `FLASK_APP=app.py` or ensure `app.py` exists |
| `ImportError: cannot import name 'X' from 'models'` | Circular import | Move imports inside functions or use late imports |
| `Address already in use` (port 5000) | Port occupied | Use `--port 5001` or kill the other process |
| `OSError: [Errno 48] Address already in use` | macOS AirPlay on 5000 | Use port 5001: `flask run --port 5001` |

## Circular Import Errors

The most common Flask issue. Happens when `app.py` imports from `models.py` and `models.py` imports from `app.py`.

**Fix: Use the application factory pattern with late imports.**

```python
# models.py — NO import of app
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()  # Not bound to app yet

# app.py
def create_app():
    app = Flask(__name__)
    from models import db  # Import INSIDE factory
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
| `TypeError: 'NoneType' is not iterable` | `None` passed to `{% for %}` | Use `{% for x in items or [] %}` or check before passing |
| Jinja2 syntax error | Wrong delimiter | Use `{{ }}` for expressions, `{% %}` for statements |

## Database Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `OperationalError: no such table` | Tables not created | Add `db.create_all()` in app context or run migrations |
| `OperationalError: table already exists` | Duplicate create | Use `db.create_all()` (safe to call repeatedly) or use migrations |
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
| CSRF token missing | No hidden CSRF field | Add `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">` |
| File upload empty | Missing `enctype` | Add `enctype="multipart/form-data"` to form tag |

## Performance Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Slow page loads | N+1 queries | Use `joinedload()` or `subqueryload()` in SQLAlchemy queries |
| Memory growing | Debug mode in production | Set `FLASK_DEBUG=0` in production |
| Static files slow | No caching headers | Configure web server (Nginx) for static file serving |

## Debug Mode

Enable detailed error pages and auto-reload during development:

```bash
flask run --debug
```

**Never enable debug mode in production** — it exposes an interactive debugger that allows arbitrary code execution.

## Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
app.logger.info('Processing request for %s', request.path)
app.logger.error('Failed to save: %s', str(e))
```
