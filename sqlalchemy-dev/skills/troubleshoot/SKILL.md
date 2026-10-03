---
name: troubleshoot
description: >
  Use when the user encounters "SQLAlchemy errors", "database error",
  "OperationalError", "IntegrityError", "DetachedInstanceError",
  "AmbiguousColumnError", "LegacyAPIWarning", "No module named psycopg",
  "SQLAlchemy not working", "migration error", "debug SQLAlchemy",
  or needs to diagnose and fix common SQLAlchemy problems.
---

# SQLAlchemy Troubleshooting

Diagnostic steps and fixes for common SQLAlchemy problems.

## Quick Diagnostics

Run these checks first:

1. **Versions and driver?** — `python -c "import sqlalchemy; print(sqlalchemy.__version__)"`; SQLAlchemy 2.1 changed the default PostgreSQL driver and the `filter_by()` and autoflush rules ([SQLAlchemy 2.1](../api-reference/references/sqlalchemy-2.1.md))
2. **Database exists?** — Check if the database file or server is accessible
3. **Tables created?** — Run `flask db upgrade` (or `alembic upgrade head`); `Base.metadata.create_all(engine)` is for tests and scripts
4. **Models imported?** — Ensure all models are imported before migrations or `create_all()` read `Base.metadata`
5. **Session clean?** — Run `session.rollback()` (`db.session.rollback()` in Flask) if in a broken state

## Connection Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `OperationalError: unable to open database file` | Wrong path or missing directory | Verify the SQLite path. Flask-SQLAlchemy resolves a relative path against the `instance/` folder (`sqlite:///app.db`); create that directory |
| `OperationalError: no such table: X` | Tables not created | Run `flask db upgrade` (or `alembic upgrade head`) |
| `OperationalError: database is locked` | SQLite concurrent writes | Use WAL mode or switch to PostgreSQL |
| `ModuleNotFoundError: No module named 'psycopg'` | The URL resolves to psycopg 3 (`postgresql+psycopg://`, or a bare `postgresql://` on SQLAlchemy 2.1) and it is not installed | `pip install "psycopg[binary]"` |
| `ModuleNotFoundError: No module named 'psycopg2'` | The URL names psycopg2 (`postgresql+psycopg2://`, or a bare `postgresql://` on SQLAlchemy 2.0) | Switch to `postgresql+psycopg://` and install `psycopg[binary]`; or install psycopg2 on purpose (see [Legacy 1.x style](../api-reference/references/legacy-1x-style.md)) |
| `ImportError: The SQLAlchemy asyncio module requires that the Python 'greenlet' library is installed` | SQLAlchemy 2.1 no longer installs `greenlet` | `pip install "sqlalchemy[asyncio]"` |
| `OperationalError: FATAL: password authentication failed` | Wrong credentials | Check DATABASE_URL user/password |
| `OperationalError: could not connect to server` | DB server not running | Start the database server |

## Integrity Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `IntegrityError: UNIQUE constraint failed` | Duplicate value on unique column | Check for existing record before insert, or catch the error |
| `IntegrityError: NOT NULL constraint failed` | Missing required field | Ensure all `Mapped[X]` (non-optional) columns have values |
| `IntegrityError: FOREIGN KEY constraint failed` | Referenced record doesn't exist, or deleting a parent that still has children | Create the parent first; for deletes use `cascade="all, delete-orphan"` on the relationship, or `ondelete="CASCADE"` on the foreign key |

SQLite ignores foreign keys unless each connection runs `PRAGMA foreign_keys=ON`, so a missing parent only raises there once you enable it:

```python
from sqlalchemy import create_engine, event

engine = create_engine("sqlite:///app.db")


@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
```

### Handling Integrity Errors

```python
from sqlalchemy.exc import IntegrityError

try:
    session.add(record)
    session.commit()
except IntegrityError:
    session.rollback()
    flash('A record with that value already exists', 'error')
```

## Session Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `DetachedInstanceError: Instance is not bound to a Session` | Reading an attribute or lazy relationship after the session closed | Load what you need inside the session (`selectinload`, `undefer`); or create the session with `expire_on_commit=False` when objects are read after `commit()` |
| `InvalidRequestError: This session's transaction has been rolled back` | Previous error left session dirty | Call `session.rollback()` before retrying |
| `RuntimeError: Working outside of application context` | No Flask app context | Wrap in `with app.app_context():` |
| `MissingGreenlet: greenlet_spawn has not been called` | A lazy load or expired-attribute refresh in async code | Load relationships up front (`selectinload`), use `expire_on_commit=False` on `AsyncSession` |
| `ArgumentError: Textual SQL expression '...' should be explicitly declared as text('...')` | A bare string passed to `execute()` | `session.execute(text("..."))` |
| `LegacyAPIWarning: The Query.get() method is considered legacy` | A legacy `Query.get()` call, including the one behind `get_or_404()` on a model's `query` attribute | `session.get(Model, pk)`, or `db.get_or_404(Model, pk)` in Flask-SQLAlchemy |
| `AmbiguousColumnError: Attribute name "id" is ambiguous` | SQLAlchemy 2.1: `select(...).join(...).filter_by(id=...)` with `id` in several entities | `.where(Entity.id == value)` |
| `InvalidRequestError: Class ... is already a dataclass` | A `MappedAsDataclass` base with Flask-SQLAlchemy 3.1.x on SQLAlchemy 2.1 ([#1420](https://github.com/pallets-eco/flask-sqlalchemy/issues/1420)) | `pip install "SQLAlchemy<2.1"`, or drop `MappedAsDataclass` |
| `MappedAnnotationError: Type annotation for "X.y" can't be correctly interpreted` | A model attribute annotated with a plain type (`int`, `list[...]`) instead of `Mapped[...]` | Annotate with `Mapped[...]`; as a stopgap set `__allow_unmapped__ = True` on the class |
| `AmbiguousForeignKeysError: Could not determine join condition` | Two foreign keys link the same pair of tables | Pass `foreign_keys=[Model.col]` to the `relationship()` |
| `SAWarning: relationship 'X.a' will copy column ... which conflicts with relationship(s)` | Two relationships write the same foreign key and are not linked | Link them with `back_populates`, or add `overlaps="..."` when the overlap is deliberate |

### Session Best Practices

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Always roll back on error
try:
    session.add(obj)
    session.commit()
except Exception:
    session.rollback()
    raise

# Load what the view needs while the session is open, not in the template
client = session.scalars(
    select(Client)
    .options(selectinload(Client.appointments))
    .where(Client.id == client_id)
).one()
```

A computed column that the page reads (`Client.visit_count` in `model-patterns`, Computed Values) is loaded in the same statement with `.options(undefer(Client.visit_count))`; the page then runs no further query.

## Migration Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Target database is not up to date` | Pending migrations | Run `flask db upgrade` |
| `Can't locate revision` | The database names a revision whose file is missing | Restore the file, check `flask db heads` / `history`; do not `stamp head` (see `cli-recipes`) |
| `Multiple head revisions are present` | Two branches each added a migration | `flask db merge -m "Merge heads" <rev1> <rev2>` |
| `No changes in schema detected` | Model changes not picked up | Import models in `env.py`; remove `create_all()` from the factory |
| Autogenerate missed a change | Limitation of autogenerate | Edit migration manually |

## Performance Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Many queries for one page | N+1 problem (lazy loading) | Use `joinedload()` or `selectinload()`; set `lazy="raise"` to find the culprits |
| Slow queries on large tables | Missing indexes | Add `index=True` to frequently filtered and joined columns, including foreign keys |
| Memory growing on bulk operations | Every row loaded as an object (`.all()`), or very many pending objects | Stream with `execution_options(yield_per=...)`, commit in batches, `session.expunge_all()` between batches, bulk `insert()` for writes (see `query-patterns`) |
| Slow `count()` on large tables | Full table scan | `select(func.count()).select_from(Model).where(...)` with a selective filter |

`expire_on_commit=False` does not reduce memory (it only keeps attributes loaded after `commit()`), and assigning it on `db.session` has no effect on the sessions it creates: pass it when the session is made, `sessionmaker(engine, expire_on_commit=False)` or `SQLAlchemy(session_options={"expire_on_commit": False})`.

### Detecting N+1 Queries

```python
# Enable SQLAlchemy query logging
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

Watch for repeated similar queries — fix with eager loading:

```python
from sqlalchemy import select
from sqlalchemy.orm import joinedload

# Before (N+1): 1 query for appointments + N queries for clients
appointments = session.scalars(select(Appointment)).all()
for appt in appointments:
    print(appt.client.name)

# After (eager): 1 query with JOIN
appointments = session.scalars(
    select(Appointment).options(joinedload(Appointment.client))
).all()
```

## Type Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `StatementError: expected string or bytes-like object` | Wrong type for column | Check the `Mapped[...]` annotation and `mapped_column` type match the data |
| `DataError: value too long for type character varying` | String exceeds `String(N)` length | Increase column size or validate input |
| `ProgrammingError: can't adapt type 'dict'` | Passing dict to non-JSON column | Use `mapped_column(JSON)` or serialize |
