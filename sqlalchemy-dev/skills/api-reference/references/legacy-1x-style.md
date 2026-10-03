# Legacy 1.x Style

This page is the only place in the plugin where the SQLAlchemy 1.x and Flask-SQLAlchemy 2.x forms are written out. Use it to read old code and translate it. New code uses the typed 2.0 style described in `model-patterns` and `query-patterns`.

## How Much of It Still Works

Measured on SQLAlchemy 2.0.54 and 2.1.3 with Flask-SQLAlchemy 3.1.1:

| Legacy form | On SQLAlchemy 2.0 and 2.1 | Use instead |
|-------------|---------------------------|-------------|
| `Model.query.get(id)`, `session.query(M).get(id)`, `Model.query.get_or_404(id)` | Works, emits `LegacyAPIWarning` (the only legacy form that warns) | `session.get(M, id)`, `db.get_or_404(M, id)` |
| `Model.query.filter_by(...).all()` / `.first()` / `.count()` / `.paginate()` / `.with_entities()`, `session.query(...)` | Works silently. `Query` is a legacy API: it gets no new features and no 2.1 changes (its `filter_by()` keeps the 2.0 behavior) | `select()` with `session.scalars()` / `session.execute()`, `db.paginate()` |
| `.isnot(None)`, `.isnot_distinct_from(...)` | Works silently, an alias | `.is_not(None)`, `.is_not_distinct_from(...)` |
| `Client.id.in_(select(subq))` after `.subquery()` | Works | `.in_(select(...))` with the statement itself |
| `engine.execute(...)`, `Query.from_self()` | Removed in 2.0: `AttributeError` | `with engine.connect() as conn: conn.execute(text(...))` |
| `session.execute("SELECT 1")` (bare string) | Removed: `ArgumentError: Textual SQL expression ... should be explicitly declared as text(...)` | `session.execute(text("SELECT 1"))` |
| `relationship("Post", backref="author")` | Works silently; the other side exists only implicitly, so type checkers and IDEs cannot see it | `back_populates` on both sides |
| `lazy=True` | Works silently, an alias for `"select"` | `lazy="select"` (the default), or a deliberate strategy |
| `lazy="subquery"`, `lazy="dynamic"` | Work silently; superseded | `lazy="selectin"`, `lazy="write_only"` |
| `db.Column(db.Integer)`, `db.relationship(...)`, `Column()` without `Mapped[...]` | Works silently on `db.Model` and on `DeclarativeBase`; nothing is type-checked | `mapped_column()`, `Mapped[...]`, `relationship()` |
| `from sqlalchemy.ext.declarative import declarative_base` | `MovedIn20Warning` | `class Base(DeclarativeBase): pass` |
| `db.session.expire_on_commit = False` | No error and no effect: the real session keeps `expire_on_commit=True` | `SQLAlchemy(session_options={"expire_on_commit": False})` or `sessionmaker(engine, expire_on_commit=False)` |
| `db.Column(db.DateTime, default=func.now())` meant as a server default | SQLAlchemy sends `now()` with each `INSERT`; rows written elsewhere get no default | `server_default=func.now()` |
| `default=datetime.utcnow` | `DeprecationWarning` since Python 3.12; naive datetime | `default=lambda: datetime.now(timezone.utc)` |
| `postgresql://` URL with `pip install psycopg2-binary` | 2.0 uses psycopg2; 2.1 uses psycopg 3 and raises `ModuleNotFoundError: No module named 'psycopg'` | `postgresql+psycopg://` with `pip install "psycopg[binary]"`; keep psycopg2 on purpose with `postgresql+psycopg2://` |
| `SQLALCHEMY_TRACK_MODIFICATIONS = False` | Harmless; Flask-SQLAlchemy 3.x defaults to `False` and does not warn | Remove it |
| `flask db stamp head` to clear a revision error | Marks the database current without running migrations | See the `cli-recipes` skill |

To find the warning in a test suite, turn the warning category into an error in `pyproject.toml` (`filterwarnings = ["error::sqlalchemy.exc.SADeprecationWarning"]`); `LegacyAPIWarning` is a subclass.

## Models

```python
# 1.x model (Flask-SQLAlchemy 2.x style)
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    posts = db.relationship("Post", backref="author", lazy=True)


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
```

```python
# 2.0 model
class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True)

    posts: Mapped[list["Post"]] = relationship(back_populates="author")


class Post(db.Model):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    author: Mapped["User"] = relationship(back_populates="posts")
```

`Mapped[str]` is `NOT NULL`, `Mapped[str | None]` is nullable; `nullable=False` becomes redundant. `backref="author"` created `Post.author` out of sight; `back_populates` declares both sides.

## Queries

```python
# 1.x queries
users = User.query.all()
user = User.query.get(1)
user = User.query.get_or_404(1)
ann = User.query.filter_by(name="Ann").first()
page = User.query.paginate(page=1, per_page=20, error_out=False)
count = db.session.query(func.count(User.id)).filter(User.name != "x").scalar()
rows = db.session.query(Post.id, Post.user_id).filter(Post.user_id.isnot(None)).all()
names = User.query.with_entities(User.name).order_by(User.name).all()
author_ids = db.session.query(Post.user_id).distinct().subquery()
authors = User.query.filter(User.id.in_(select(author_ids))).all()
```

```python
# 2.0 queries
users = db.session.scalars(db.select(User)).all()
user = db.session.get(User, 1)
user = db.get_or_404(User, 1)
ann = db.session.scalars(db.select(User).filter_by(name="Ann")).first()
page = db.paginate(db.select(User), page=1, per_page=20, error_out=False)
count = db.session.scalar(db.select(func.count(User.id)).where(User.name != "x"))
rows = db.session.execute(db.select(Post.id, Post.user_id).where(Post.user_id.is_not(None))).all()
names = db.session.scalars(db.select(User.name).order_by(User.name)).all()
author_ids = db.select(Post.user_id).distinct()
authors = db.session.scalars(db.select(User).where(User.id.in_(author_ids))).all()
```

`.filter()` still exists on a `select()` as an alias of `.where()`; write `.where()`.

## Plain SQLAlchemy 1.x

```python
# 1.x, without Flask
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

Base = declarative_base()


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))


engine = create_engine("sqlite://")
Base.metadata.create_all(engine)

with sessionmaker(engine)() as session:
    session.add(Item(name="a"))
    session.commit()
    item = session.query(Item).get(1)
    items = session.query(Item).filter(Item.name == "a").all()
    total = session.query(Item).count()
```

```python
# 2.0 equivalent
from sqlalchemy import String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(String(50))


engine = create_engine("sqlite://")
Base.metadata.create_all(engine)

with Session(engine) as session:
    session.add(Item(name="a"))
    session.commit()
    item = session.get(Item, 1)
    items = session.scalars(select(Item).where(Item.name == "a")).all()
    total = session.scalar(select(func.count()).select_from(Item))
```

## Migrating a Codebase Step by Step

1. **Models first, or queries first: both orders work.** `Column()` attributes keep working on a `DeclarativeBase` model next to `Mapped[...]` ones, and `Model.query` keeps working on a model whose columns are already typed. Convert one module at a time and keep the tests green.
2. **Do not half-annotate.** On a `DeclarativeBase` a plain annotation such as `kids: list["Post"] = relationship(...)` or `id: int = mapped_column(...)` raises `MappedAnnotationError`. Either use `Mapped[...]` or, as a temporary bridge, set `__allow_unmapped__ = True` on the class.
3. **Turn the warnings into errors** (see above) so a stray `Query.get()` fails the build instead of waiting for the next major release.
4. **Replace queries by pattern**, with search and replace plus review: `Model.query.get(x)` becomes `db.session.get(Model, x)`; `Model.query.filter_by(...).all()` becomes `db.session.scalars(db.select(Model).filter_by(...)).all()`. A `.query.` call chained after a join or a `with_entities()` needs a manual rewrite.
5. **Replace `backref` last**: for each `backref="x"` add the explicit attribute on the other model and switch both sides to `back_populates`.
6. **Move to SQLAlchemy 2.1** only after the code runs clean on 2.0.x: [SQLAlchemy 2.1](sqlalchemy-2.1.md).
