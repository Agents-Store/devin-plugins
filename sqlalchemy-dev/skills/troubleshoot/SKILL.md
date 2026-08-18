---
name: troubleshoot
description: >
  Use when the user encounters "SQLAlchemy errors", "database error",
  "OperationalError", "IntegrityError", "DetachedInstanceError",
  "SQLAlchemy not working", "migration error", "debug SQLAlchemy",
  or needs to diagnose and fix common SQLAlchemy problems.
---

# SQLAlchemy Troubleshooting

Diagnostic steps and fixes for common SQLAlchemy problems.

## Quick Diagnostics

Run these checks first:

1. **Database exists?** — Check if the database file or server is accessible
2. **Tables created?** — Run `flask db upgrade` or `db.create_all()`
3. **Models imported?** — Ensure all models are imported before `create_all()`
4. **Session clean?** — Run `db.session.rollback()` if in a broken state

## Connection Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `OperationalError: unable to open database file` | Wrong path or missing directory | Verify `SQLALCHEMY_DATABASE_URI` path; create `instance/` dir |
| `OperationalError: no such table: X` | Tables not created | Run `db.create_all()` or `flask db upgrade` |
| `OperationalError: database is locked` | SQLite concurrent writes | Use WAL mode or switch to PostgreSQL |
| `ModuleNotFoundError: psycopg2` | Missing PostgreSQL driver | `pip install psycopg2-binary` |
| `OperationalError: FATAL: password authentication failed` | Wrong credentials | Check DATABASE_URL user/password |
| `OperationalError: could not connect to server` | DB server not running | Start the database server |

## Integrity Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `IntegrityError: UNIQUE constraint failed` | Duplicate value on unique column | Check for existing record before insert |
| `IntegrityError: NOT NULL constraint failed` | Missing required field | Ensure all `nullable=False` columns have values |
| `IntegrityError: FOREIGN KEY constraint failed` | Referenced record doesn't exist | Verify parent record exists before creating child |

### Handling Integrity Errors

```python
from sqlalchemy.exc import IntegrityError

try:
    db.session.add(record)
    db.session.commit()
except IntegrityError:
    db.session.rollback()
    flash('A record with that value already exists', 'error')
```

## Session Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `DetachedInstanceError: Instance is not bound to a Session` | Accessing object after session closed | Access all attributes within session scope |
| `InvalidRequestError: This session's transaction has been rolled back` | Previous error left session dirty | Call `db.session.rollback()` before retrying |
| `RuntimeError: Working outside of application context` | No Flask app context | Wrap in `with app.app_context():` |

### Session Best Practices

```python
# Always rollback on error
try:
    db.session.add(obj)
    db.session.commit()
except Exception:
    db.session.rollback()
    raise

# Access relationships before returning from view
client = Client.query.get(id)
name = client.name          # Access here, not in template
visits = client.visit_count  # Computed property — access here
```

## Migration Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Target database is not up to date` | Pending migrations | Run `flask db upgrade` |
| `Can't locate revision` | Broken migration chain | `flask db stamp head` to reset |
| `No changes in schema detected` | Model changes not picked up | Import models in `env.py` |
| Autogenerate missed a change | Limitation of autogenerate | Edit migration manually |

## Performance Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Many queries for one page | N+1 problem (lazy loading) | Use `joinedload()` or `selectinload()` |
| Slow queries on large tables | Missing indexes | Add `index=True` to frequently filtered columns |
| Memory growing on bulk operations | Objects accumulate in session | Use `db.session.expire_on_commit = False` or batch |
| Slow `count()` on large tables | Full table scan | Use `func.count()` with specific filters |

### Detecting N+1 Queries

```python
# Enable SQLAlchemy query logging
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

Watch for repeated similar queries — fix with eager loading:

```python
from sqlalchemy.orm import joinedload

# Before (N+1): 1 query for appointments + N queries for clients
appointments = Appointment.query.all()

# After (eager): 1 query with JOIN
appointments = Appointment.query.options(
    joinedload(Appointment.client)
).all()
```

## Type Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `StatementError: expected string or bytes-like object` | Wrong type for column | Check `db.Column` type matches the data |
| `DataError: value too long for type character varying` | String exceeds `String(N)` length | Increase column size or validate input |
| `ProgrammingError: can't adapt type 'dict'` | Passing dict to non-JSON column | Use `db.Column(db.JSON)` or serialize |
