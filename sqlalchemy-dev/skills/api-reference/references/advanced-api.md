# SQLAlchemy Advanced API Reference

Examples use the `Base` and models from the `model-patterns` skill.

## Alembic Migration API

```bash
# Flask-Migrate commands
flask db init                         # Initialize migrations (once)
flask db migrate -m "Description"     # Auto-generate migration
flask db upgrade                      # Apply all pending migrations
flask db downgrade                    # Revert last migration
flask db current                      # Show current revision
flask db heads                        # Show the newest revision(s); more than one means a branch
flask db history                      # Show migration history
flask db check                        # Exit non-zero when the models differ from the schema
flask db merge -m "Merge" <rev> <rev> # Join two heads
```

```bash
# Standalone Alembic commands
alembic init alembic                      # Initialize (alembic.ini + env.py)
alembic init --template pyproject alembic # Initialize with settings in pyproject.toml (Alembic 1.16+)
alembic revision --autogenerate -m "msg"  # Generate migration
alembic upgrade head                      # Apply all
alembic upgrade head --sql                # Print the SQL instead of running it (offline mode)
alembic downgrade -1                      # Revert one
alembic current                           # Current revision
alembic heads                             # Newest revision(s)
alembic history                           # History
alembic check                             # CI gate: fails if autogenerate would produce a migration
```

`stamp` writes a revision into `alembic_version` without running anything. Reach for it only to adopt an existing database or to repair the version table on purpose (`flask db stamp <revision>`); `stamp head` on a database that is behind marks it current and hides every missing change. See the `cli-recipes` skill.

## Table Arguments

```python
from sqlalchemy import CheckConstraint, Index, UniqueConstraint


class Reading(Base):
    __tablename__ = "readings"
    __table_args__ = (
        UniqueConstraint("col_a", "col_b", name="uq_a_b"),
        Index("idx_col_a", "col_a"),
        CheckConstraint("price >= 0", name="positive_price"),
        {"schema": None},  # a dict, when present, must be the last item
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    col_a: Mapped[str] = mapped_column(String(20))
    col_b: Mapped[str] = mapped_column(String(20))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
```

Replace `{"schema": None}` with `{"schema": "myschema"}` to place the table in a schema. With a naming convention on `Base.metadata` (see `model-patterns`), a `CheckConstraint` must carry a `name=`.

## Hybrid Properties

A `hybrid_property` works on an instance (Python) and on the class (SQL expression):

```python
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import ColumnElement


class Person(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))

    @hybrid_property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @full_name.inplace.expression
    @classmethod
    def _full_name_expression(cls) -> ColumnElement[str]:
        return cls.first_name + " " + cls.last_name
```

`select(Person).where(Person.full_name == "Ada Lovelace")` renders `first_name || ' ' || last_name`. The `inplace` form keeps type checkers happy; the older `@full_name.expression` decorator still works.

## Events

```python
from sqlalchemy import event
from sqlalchemy.orm import Session


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str | None] = mapped_column(String(20))


@event.listens_for(Account, "before_insert")
def set_defaults(mapper, connection, target):
    if not target.status:
        target.status = "new"


@event.listens_for(Session, "after_commit")
def after_commit(session):
    # Post-commit logic: runs once per commit, for every Session
    pass
```

Listening on the `Session` class covers every session, including `db.session` in Flask-SQLAlchemy. Do not issue ORM operations on the session inside flush-time events; use the `connection` they receive.

## Async SQLAlchemy

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine("postgresql+asyncpg://user:password@host/dbname")
# psycopg 3 also supports asyncio: "postgresql+psycopg://user:password@host/dbname"
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
# on application shutdown: await engine.dispose()


async def get_users() -> list[User]:
    async with async_session() as session:
        result = await session.scalars(select(User))
        return result.all()
```

- SQLAlchemy 2.1 no longer installs `greenlet` by default: asyncio needs `pip install "sqlalchemy[asyncio]"`. Without it, importing `sqlalchemy.ext.asyncio` fails with `ImportError: The SQLAlchemy asyncio module requires that the Python 'greenlet' library is installed`.
- Use `expire_on_commit=False` with `AsyncSession`: an expired attribute would need a lazy load, which is not allowed outside `await`.
- Lazy loads raise `MissingGreenlet` in async code. Load relationships up front with `selectinload()` or declare them `lazy="raise"` / `"selectin"`, or use `await session.run_sync(...)`.

## Write-Only Collections

For a collection too large to ever load, map it `WriteOnlyMapped`: it never loads, and you query it with `select()`:

```python
from sqlalchemy import select
from sqlalchemy.orm import WriteOnlyMapped


class Feed(Base):
    __tablename__ = "feeds"

    id: Mapped[int] = mapped_column(primary_key=True)
    entries: WriteOnlyMapped["Entry"] = relationship(back_populates="feed")


class Entry(Base):
    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    feed_id: Mapped[int] = mapped_column(ForeignKey("feeds.id"))
    title: Mapped[str] = mapped_column(String(200))

    feed: Mapped["Feed"] = relationship(back_populates="entries")
```

```python
feed = Feed()
feed.entries.add(Entry(title="first"))  # add() / remove() work without loading
session.add(feed)
session.flush()

recent = session.scalars(feed.entries.select().order_by(Entry.id.desc()).limit(10)).all()
```

## Bulk and Streaming Operations

Bulk insert, update and delete with dictionaries are in `query-patterns` (Bulk Operations). To read a large result without holding it all in memory, stream in batches:

```python
for client in session.scalars(select(Client).execution_options(yield_per=500)):
    ...  # one batch of 500 rows is fetched at a time

for batch in session.scalars(select(Client).execution_options(yield_per=500)).partitions():
    ...  # lists of up to 500 objects
```

`yield_per` cannot be combined with a `joinedload` of a collection (SQLAlchemy raises `InvalidRequestError`); use `selectinload`, which loads each batch's collections with one extra query per batch.
