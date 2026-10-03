---
name: cli-recipes
description: >
  Use when the user asks about "Flask CLI", "flask run", "flask shell",
  "flask routes", "Flask command line", "custom Flask CLI command",
  "run Flask from terminal", or needs ready-to-use Flask CLI commands.
---

# Flask CLI Recipes

Ready-to-use CLI commands for Flask development.

## Running the Application

```bash
# Development server (debug mode: reloader + interactive debugger)
flask --app app run --debug

# Call the factory explicitly (literal arguments are allowed inside the parentheses)
flask --app 'app:create_app()' run --debug

# Specify host and port
flask --app app run --host=0.0.0.0 --port=5001

# Same through environment variables (FLASK_APP, FLASK_DEBUG, FLASK_RUN_PORT)
FLASK_APP=app FLASK_DEBUG=1 flask run

# Extra dotenv file, loaded in addition to .env and .flaskenv
flask --env-file .env.local --app app run
```

`--app` and `--debug` are options of the top-level `flask` command, so they also work for other commands: `flask --app app --debug shell`. Debug mode comes only from `--debug` / `FLASK_DEBUG`; `FLASK_ENV` was removed in Flask 2.3 and is ignored.

## Interactive Shell

```bash
# Start Flask shell with app context
flask shell
```

Inside the shell, the app context is automatically available:

```pycon
>>> from extensions import db
>>> from models import User, Client
>>> db.session.scalars(db.select(User)).all()
>>> db.session.add(User(name='Test', email='test@example.com'))
>>> db.session.commit()
```

## Route Inspection

```bash
# List all registered routes
flask routes

# Output:
# Endpoint         Methods    Rule
# ---------------  ---------  -----------------------
# auth.login       GET, POST  /login
# auth.register    GET, POST  /register
# clients.clients  GET        /clients
# static           GET        /static/<path:filename>
```

`flask routes --sort rule` and `--all-methods` change the ordering and include `HEAD`/`OPTIONS`.

## Database Migrations (Flask-Migrate)

```bash
# Initialize migrations (once)
flask db init

# Create migration after model changes
flask db migrate -m "Add birthday column to clients"

# Apply migrations
flask db upgrade

# Rollback last migration
flask db downgrade

# Show current migration
flask db current

# Show migration history
flask db history
```

## Custom CLI Commands

Register custom commands on `app.cli` (or `blueprint.cli`) with Click decorators. Since Flask 2.2 an app context is already active inside them, so `@with_appcontext` is no longer needed:

```python
# app.py: imports at the top of the file
from datetime import datetime, timedelta

import click

# inside create_app() (the factory pattern has no module-level `app`)
@app.cli.command('seed')
def seed_db():
    """Seed the database with sample data."""
    from extensions import db
    from models import User
    # '!' matches no password: the seeded account cannot sign in until a real hash is set
    user = User(name='Admin', email='admin@example.com', password_hash='!')
    db.session.add(user)
    db.session.commit()
    click.echo('Database seeded.')

@app.cli.command('cleanup')
@click.argument('days', default=30)
def cleanup_old_data(days):
    """Remove records older than N days."""
    cutoff = datetime.now() - timedelta(days=days)
    # ...
    click.echo(f'Cleaned up records older than {days} days.')
```

```bash
flask seed
flask cleanup 60
```

`@with_appcontext` (from `flask.cli`) is still needed for a plain `click.command` that is not registered on `app.cli`, for example one an extension ships through the `flask.commands` entry point; such a command gets no automatic app context.

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `FLASK_APP` | Application module (same as `--app`) | `app.py` or `wsgi.py` |
| `FLASK_DEBUG` | Enable debug mode (same as `--debug`) | `0` |
| `FLASK_RUN_HOST` | Server host | `127.0.0.1` |
| `FLASK_RUN_PORT` | Server port | `5000` |

`FLASK_ENV` is not in this table: it was removed in Flask 2.3 and is ignored. To switch between development, production and test configuration use an application-level variable such as `APP_ENV` (see the `app-patterns` skill).

Use a `.flaskenv` file (with `python-dotenv` installed) for public defaults and `.env` for private values; both are loaded by the `flask` command, and `--env-file` adds another file (`-e path` wins over the defaults):

```bash
# .flaskenv
FLASK_APP=app
APP_ENV=development
FLASK_DEBUG=1
FLASK_RUN_PORT=5001
```

Dotenv files are only read by the `flask` command and `app.run()`. In production (gunicorn, waitress) call `flask.cli.load_dotenv()` yourself or set real environment variables.

## Production Server

```bash
# Gunicorn (Linux/macOS)
pip install gunicorn
gunicorn "app:create_app()" --bind 0.0.0.0:8000 --workers 4

# Waitress (Windows-compatible)
pip install waitress
waitress-serve --call "app:create_app"
```
