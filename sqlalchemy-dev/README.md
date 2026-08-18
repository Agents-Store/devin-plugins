# sqlalchemy-dev (Devin plugin)

SQLAlchemy dev plugin for Agents Store. Model definition patterns, relationship mapping, query optimization, Alembic migrations, and troubleshooting for developers building with SQLAlchemy 2.0+.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (6)

- `api-reference` — Use when the user asks for "SQLAlchemy API reference", "SQLAlchemy Column types", "SQLAlchemy session methods", "db.session API", "SQLAlchemy relationship options", or needs specific SQLAlchemy framework API details.

- `cli-recipes` — Use when the user asks about "Alembic commands", "database migrations", "flask db migrate", "flask db upgrade", "create migration", "rollback migration", "SQLAlchemy CLI", or needs ready-to-use database migration commands.

- `model-patterns` — Use when the user asks about "SQLAlchemy models", "define database model", "SQLAlchemy relationships", "one-to-many relationship", "many-to-many", "SQLAlchemy column types", "model constraints", "Flask-SQLAlchemy model", or needs patterns for defining database models with SQLAlchemy.

- `query-patterns` — Use when the user asks about "SQLAlchemy queries", "filter records", "SQLAlchemy select", "join tables", "aggregate query", "order by", "pagination", "N+1 query problem", "eager loading", "SQLAlchemy session", or needs patterns for querying data with SQLAlchemy.

- `setup` — Use when the user asks to "verify SQLAlchemy setup", "check database connection", "is SQLAlchemy configured correctly", "test database setup", or needs to confirm that SQLAlchemy is properly initialized in their Python project.

- `troubleshoot` — Use when the user encounters "SQLAlchemy errors", "database error", "OperationalError", "IntegrityError", "DetachedInstanceError", "SQLAlchemy not working", "migration error", "debug SQLAlchemy", or needs to diagnose and fix common SQLAlchemy problems.


## Not carried over

- 1 agent(s) — Devin plugins do not support agents

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/sqlalchemy-dev
