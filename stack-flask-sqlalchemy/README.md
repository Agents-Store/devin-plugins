# stack-flask-sqlalchemy (Devin plugin)

Flask + SQLAlchemy architecture plugin. How the application factory, the Flask-SQLAlchemy session, Alembic migrations and Jinja2 templates fit together: where db is created, the app context, the transaction boundary, expire_on_commit, N+1 at the route-to-template edge, and a full-feature recipe. Tool knowledge comes from its dependencies flask-dev and sqlalchemy-dev.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (2)

- `full-feature` — Use when the user asks to "add a new feature", "create a new page", "build CRUD for a new entity", "add a new section to the app", "implement a full feature end-to-end", or needs a step-by-step recipe for building a complete feature across Flask + SQLAlchemy layers.

- `layers-and-boundaries` — Use when the user asks about "Flask SQLAlchemy architecture", "where to create db in Flask", "Flask app context and SQLAlchemy session", "when to commit in Flask", "Flask transaction boundary", "expire_on_commit in Flask-SQLAlchemy", "DetachedInstanceError in Flask", "Working outside of application context", "N+1 in a Jinja template", "lazy raise in Flask", "data saved in tests but lost in production", or needs the rules for where each layer of a Flask + SQLAlchemy app starts and ends.


## Not carried over

- 1 agent(s) — Devin plugins do not support agents

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/stack-flask-sqlalchemy
