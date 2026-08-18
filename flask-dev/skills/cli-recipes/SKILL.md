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
# Development server (with auto-reload)
flask run --debug

# Specify host and port
flask run --host=0.0.0.0 --port=5001

# With environment variables
FLASK_APP=app.py FLASK_DEBUG=1 flask run

# Using python directly
python app.py
```

## Interactive Shell

```bash
# Start Flask shell with app context
flask shell
```

Inside the shell, the app context is automatically available:

```python
>>> from models import db, User, Client
>>> User.query.all()
>>> db.session.add(User(name='Test', email='test@example.com'))
>>> db.session.commit()
```

## Route Inspection

```bash
# List all registered routes
flask routes

# Output:
# Endpoint              Methods  Rule
# --------------------  -------  -----------------------
# auth.login            GET,POST /login
# auth.register         GET,POST /register
# clients.clients       GET      /clients
# static                GET      /static/<path:filename>
```

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

Register custom commands using Click decorators:

```python
import click
from flask.cli import with_appcontext

@app.cli.command('seed')
@with_appcontext
def seed_db():
    """Seed the database with sample data."""
    from models import db, User
    user = User(name='Admin', email='admin@example.com')
    db.session.add(user)
    db.session.commit()
    click.echo('Database seeded.')

@app.cli.command('cleanup')
@click.argument('days', default=30)
@with_appcontext
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

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `FLASK_APP` | Application module | `app.py` or `wsgi.py` |
| `FLASK_DEBUG` | Enable debug mode | `0` |
| `FLASK_ENV` | Environment name | `production` |
| `FLASK_RUN_HOST` | Server host | `127.0.0.1` |
| `FLASK_RUN_PORT` | Server port | `5000` |

Use a `.flaskenv` file (with `python-dotenv` installed) to set defaults:

```bash
# .flaskenv
FLASK_APP=app.py
FLASK_DEBUG=1
FLASK_RUN_PORT=5001
```

## Production Server

```bash
# Gunicorn (Linux/macOS)
pip install gunicorn
gunicorn "app:create_app()" --bind 0.0.0.0:8000 --workers 4

# Waitress (Windows-compatible)
pip install waitress
waitress-serve --call "app:create_app"
```
