# stack-flask-sqlalchemy-dev (Devin plugin)

Flask + SQLAlchemy stack dev plugin for Agents Store. Integration patterns for app factory wiring, blueprint-model coordination, Flask-Login + SQLAlchemy auth, Jinja2 + query data, and full-feature recipes.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (4)

- `auth-integration` — Use when the user asks about "Flask-Login with SQLAlchemy", "user authentication", "login registration flow", "password hashing", "protect routes", "current_user with database", "session management Flask", or needs patterns for integrating Flask-Login authentication with SQLAlchemy user models.

- `flask-sqlalchemy-wiring` — Use when the user asks about "connect Flask to SQLAlchemy", "Flask-SQLAlchemy wiring", "blueprint model integration", "pass query data to template", "form to database", "render database data in template", "Flask model view pattern", or needs patterns for connecting Flask routes, SQLAlchemy models, and Jinja2 templates.

- `full-feature` — Use when the user asks to "add a new feature", "create a new page", "build CRUD for a new entity", "add a new section to the app", "implement a full feature end-to-end", or needs a step-by-step recipe for building a complete feature across Flask + SQLAlchemy layers.

- `init-project` — Use when the user asks to "set up Flask project", "initialize Flask SQLAlchemy project", "scaffold Flask app", "create Flask project structure", "bootstrap Flask application", or needs to set up a new Flask + SQLAlchemy project from scratch with all integrations wired.


## Not carried over

- 1 agent(s) — Devin plugins do not support agents

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/stack-flask-sqlalchemy-dev
