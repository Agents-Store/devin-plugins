---
name: setup
description: >
  Use when the user asks to "verify Flask project setup", "check Flask structure",
  "is my Flask app set up correctly", "validate Flask project", or needs to confirm
  that a Flask project follows recommended patterns and has correct file structure.
---

# Flask Project Setup Verification

Verify that a Flask project is correctly structured and follows recommended patterns.

## Project Structure Check

Inspect the project root for these expected elements:

| Item | Purpose | Required? |
|------|---------|-----------|
| `app.py` or `wsgi.py` | Application entry point with factory function | Yes |
| `requirements.txt` or `pyproject.toml` | Python dependencies | Yes |
| `models.py` or `models/` | SQLAlchemy models | If using DB |
| `routes/` or `blueprints/` | Blueprint modules | Recommended |
| `templates/` | Jinja2 HTML templates | If rendering HTML |
| `static/` | CSS, JS, images | If serving static files |
| `instance/` | Instance-specific config and SQLite DB | Common |
| `.env` or `config.py` | Configuration | Recommended |

## Verification Steps

### 1. Check Application Factory

Read the main app file and verify it uses the application factory pattern:

```python
# Expected pattern
def create_app():
    app = Flask(__name__)
    app.config.from_object(...)
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    # Register blueprints
    app.register_blueprint(auth_bp)
    return app
```

If the app uses a global `app = Flask(__name__)` instead, flag it — the factory pattern is strongly recommended for testability and multiple instances.

### 2. Check Dependencies

Read `requirements.txt` or `pyproject.toml` and verify core Flask packages:

| Package | Purpose |
|---------|---------|
| `Flask` | Core framework |
| `Flask-SQLAlchemy` | Database ORM integration |
| `Flask-Login` | Session-based authentication |
| `Flask-WTF` | Form handling and CSRF (optional) |
| `Flask-Migrate` | Database migrations via Alembic (recommended) |
| `python-dotenv` | Environment variable loading (recommended) |
| `gunicorn` | Production WSGI server (recommended) |

### 3. Check Blueprint Registration

Verify that routes are organized into blueprints and registered in the factory:

```python
# In routes/auth.py
auth_bp = Blueprint('auth', __name__)

# In app.py create_app()
app.register_blueprint(auth_bp)
```

### 4. Check Configuration

Verify that sensitive values use environment variables, not hardcoded strings:

```python
# Good
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Bad — hardcoded secret
app.config['SECRET_KEY'] = 'my-secret-key'
```

### 5. Common Setup Issues

| Issue | Symptom | Fix |
|-------|---------|-----|
| No app factory | Tests fail, circular imports | Wrap in `create_app()` function |
| Hardcoded `SECRET_KEY` | Security risk | Use `os.environ.get('SECRET_KEY')` |
| Missing `__init__.py` in routes/ | Import errors | Add empty `__init__.py` |
| No `.gitignore` for `instance/` | Database committed to git | Add `instance/` to `.gitignore` |
| No `Flask-Migrate` | Schema changes drop data | Add Alembic migrations |

## What This Skill Does NOT Cover

- Creating a new Flask project from scratch (see app-patterns skill)
- Database model design (see sqlalchemy-dev plugin)
- Deployment configuration (belongs in project template)
