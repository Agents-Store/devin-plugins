---
name: api-reference
description: >
  Use when the user asks for "SQLAlchemy API reference", "mapped_column options",
  "SQLAlchemy column types", "SQLAlchemy session methods", "db.session API",
  "SQLAlchemy relationship options", "lazy loading strategies", or needs
  specific SQLAlchemy framework API details.
disable-model-invocation: true
---

# SQLAlchemy API Reference

Curated SQLAlchemy 2.0+ API in the typed style (`DeclarativeBase`, `Mapped`, `mapped_column`, `select`). For full docs, see https://docs.sqlalchemy.org/. The examples use the `Base` from the `model-patterns` skill.

| Reference | Covers |
|-----------|--------|
| `references/advanced-api.md` | Alembic commands, table arguments, hybrid properties, events, async, write-only collections, streaming |
| `references/sqlalchemy-2.1.md` | What changes in SQLAlchemy 2.1 and how to migrate from 2.0 |
| `references/legacy-1x-style.md` | Legacy 1.x style: old forms and their 2.0 replacements |

## Column Types

Annotated by Python type, with an explicit SQL type where the default is not enough:

```python
import datetime as dt
import uuid
from decimal import Decimal

from sqlalchemy import JSON, BigInteger, DateTime, Enum, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class TypeTour(Base):
    __tablename__ = "type_tour"

    id: Mapped[int] = mapped_column(primary_key=True)            # INTEGER
    big: Mapped[int] = mapped_column(BigInteger)                 # BIGINT
    code: Mapped[str] = mapped_column(String(20))                # VARCHAR(20)
    body: Mapped[str] = mapped_column(Text)                      # TEXT (unlimited)
    flag: Mapped[bool]                                           # BOOLEAN
    ratio: Mapped[float]                                         # FLOAT (DOUBLE on 2.1)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))       # NUMERIC(10, 2), exact
    born: Mapped[dt.date]                                        # DATE
    opens: Mapped[dt.time]                                       # TIME
    seen_at: Mapped[dt.datetime]                                 # TIMESTAMP, no time zone
    stamped_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True))  # TIMESTAMP WITH TIME ZONE
    blob: Mapped[bytes]                                          # BLOB / BYTEA (LargeBinary)
    uid: Mapped[uuid.UUID]                                       # native UUID where supported
    meta: Mapped[dict] = mapped_column(JSON)                     # JSON (PostgreSQL, MySQL, SQLite)
    kind: Mapped[str] = mapped_column(Enum("a", "b", name="kind"))  # enum of strings
```

`Mapped[X | None]` makes any of these nullable. A bare `Mapped[dict]` has no default type; pass `JSON`.

## Column Options

```python
from sqlalchemy import ForeignKey, func


class Options(Base):
    __tablename__ = "options"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))                        # NOT NULL (from Mapped[str])
    nickname: Mapped[str | None] = mapped_column(String(100))             # nullable
    email: Mapped[str] = mapped_column(String(120), unique=True)          # UNIQUE
    status: Mapped[str] = mapped_column(String(20), default="new")        # Python-side default at INSERT
    created_at: Mapped[dt.datetime] = mapped_column(server_default=func.now())  # database-side default
    touched_at: Mapped[dt.datetime | None] = mapped_column(onupdate=func.now()) # applied on UPDATE
    hits: Mapped[int] = mapped_column(index=True)                         # CREATE INDEX
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))  # foreign key
    notes: Mapped[str | None] = mapped_column(Text, deferred=True)        # loaded only when accessed
    slug: Mapped[str | None] = mapped_column(String(50), comment="URL slug")
```

`default=` is applied by SQLAlchemy in Python when it builds the `INSERT` (the value, a callable or a SQL expression is sent as a parameter); `server_default=` is part of the table definition, so the database fills it for any writer. Use `server_default=func.now()` for a database timestamp.

## Session Methods

| Method | Purpose |
|--------|---------|
| `session.add(obj)` / `session.add_all([a, b])` | Stage new objects for INSERT |
| `session.delete(obj)` | Stage for DELETE |
| `session.get(Model, pk)` | Get by primary key (identity map first), or `None` |
| `session.scalars(stmt)` | Execute, return a `ScalarResult` of the first column (entities) |
| `session.scalar(stmt)` | Execute, return the first column of the first row, or `None` |
| `session.execute(stmt)` | Execute a select/insert/update/delete, return a `Result` of rows |
| `session.commit()` | Flush and commit the transaction |
| `session.rollback()` | Roll back the transaction (required after a failed flush) |
| `session.flush()` | Send pending changes to the database without committing |
| `session.begin()` | Context manager: commit on success, roll back on error |
| `session.begin_nested()` | `SAVEPOINT` |
| `session.merge(obj)` | Copy the state of a detached object onto the persistent one |
| `session.refresh(obj)` | Reload attributes from the database |
| `session.expire(obj)` | Mark attributes stale; the next access reloads them |
| `session.expunge(obj)` / `session.expunge_all()` | Detach objects from the session |
| `session.close()` | Release the connection and detach everything |

Session constructor options worth knowing: `Session(engine, expire_on_commit=False)` keeps attributes loaded after `commit()` (use it for async sessions and for objects read after the session ends), `autoflush=False` stops implicit flushes before queries.

## Relationship Options

```python
from sqlalchemy.orm import relationship


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="project",           # explicit bidirectional pair
        lazy="selectin",                    # load strategy
        cascade="all, delete-orphan",       # children follow the parent
        order_by="Task.position",           # default ordering of the collection
        passive_deletes=True,               # let ON DELETE CASCADE do the work
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(default=0)

    project: Mapped["Project"] = relationship(back_populates="tasks")
```

| Option | Meaning |
|--------|---------|
| `back_populates="attr"` | Name of the attribute on the other class (SQLAlchemy 2.1 also accepts the attribute itself or a lambda) |
| `lazy="select"` | Default. Query on first access (the old boolean spellings are aliases; see Legacy 1.x style) |
| `lazy="selectin"` | Second `SELECT ... IN (...)` loads the collection for all parents: the usual choice for collections |
| `lazy="joined"` | `LEFT OUTER JOIN` in the parent query: for small many-to-one targets |
| `lazy="raise"` / `"raise_on_sql"` | Raise on lazy access (`raise_on_sql` still allows loads from the identity map) |
| `lazy="write_only"` | Never loaded; query and modify through `WriteOnlyMapped` (see `references/advanced-api.md`) |
| `lazy="subquery"`, `"dynamic"` | Superseded by `"selectin"` and `"write_only"` |
| `cascade="all, delete-orphan"` | Delete children with the parent and when they leave the collection |
| `uselist=False` | Scalar one-to-one (implied by a non-list annotation) |
| `order_by="Model.name"` | Default ordering |
| `foreign_keys=[Model.parent_id]` | Pick the foreign key when several exist or for self-reference |
| `secondary="table_name"` | Many-to-many association table |
| `remote_side=[id]` | Marks the "one" side of a self-referential relationship |
| `passive_deletes=True` | Do not load children to delete them; rely on the database cascade |
| `viewonly=True` | Read-only relationship (never writes) |

## Select Statement Methods

| Method | Purpose |
|--------|---------|
| `select(Model)` / `select(Model.col, ...)` | Entity or column statement |
| `.where(expr, ...)` | Filter (several arguments are ANDed) |
| `.filter_by(k=v)` | Keyword equality filter against one entity |
| `.order_by(Model.k.desc())` | Order results |
| `.limit(10)` / `.offset(20)` | Page through results |
| `.join(Model.rel)` / `.join(Other, on)` | Join; `isouter=True` for LEFT OUTER |
| `.group_by(...)` / `.having(...)` | Aggregation |
| `.distinct()` | `SELECT DISTINCT` |
| `.options(selectinload(...))` | Loader options |
| `.subquery()` / `.cte()` | Use as FROM element / common table expression |
| `.scalar_subquery()` | One-column, one-row subquery usable as an expression |
| `.exists()` | `EXISTS (...)` expression |
| `.with_for_update()` | `SELECT ... FOR UPDATE` row lock |
| `.execution_options(yield_per=N)` | Stream results in batches |

Result access: `.all()`, `.first()`, `.one()`, `.one_or_none()`, `.unique()` (required after `joinedload` of a collection), `.mappings()` (rows as dict-like objects), `.partitions(N)`.

## Aggregate Functions

```python
from sqlalchemy import func, select

select(
    func.count(Spending.id),
    func.sum(Spending.amount),
    func.avg(Spending.amount),
    func.min(Spending.spent_on),
    func.max(Spending.spent_on),
    func.coalesce(func.sum(Spending.amount), 0),  # SUM over no rows is NULL
)
```

## Flask-SQLAlchemy Equivalents

| Plain SQLAlchemy | Flask-SQLAlchemy 3.1 |
|------------------|----------------------|
| `Session(engine)` | `db.session` (scoped to the app context) |
| `select(Model)` | `db.select(Model)` |
| `session.get(Model, pk)` | `db.session.get(Model, pk)` |
| `session.get(Model, pk)` or 404 | `db.get_or_404(Model, pk)` |
| first row or 404 | `db.first_or_404(stmt)` |
| exactly one row or 404 | `db.one_or_404(stmt)` |
| `limit` / `offset` + count | `db.paginate(stmt, page=1, per_page=20)` |
| `Base.metadata.create_all(engine)` | `db.create_all()` (in an app context) |
| `class Base(DeclarativeBase)` | `SQLAlchemy(model_class=Base)`, models subclass `db.Model` |
| `sessionmaker(engine, expire_on_commit=False)` | `SQLAlchemy(session_options={"expire_on_commit": False})` |

Install Flask-SQLAlchemy with `"SQLAlchemy<2.1"` (see `model-patterns`).
