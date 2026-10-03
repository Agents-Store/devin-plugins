---
name: setup
description: >
  Use when the user asks to "verify SQLAlchemy setup", "check database connection",
  "is SQLAlchemy configured correctly", "test database setup", "which SQLAlchemy
  version", "SQLAlchemy 2.1", or needs to confirm that SQLAlchemy is properly
  initialized in their Python project.
---

# SQLAlchemy Setup Verification

Verify that SQLAlchemy is correctly configured and the database connection works.

## Verification Steps

### 1. Check Versions and Dependencies

Read `requirements.txt` or `pyproject.toml` and decide the SQLAlchemy line first:

| Situation | Pin |
|-----------|-----|
| New plain-SQLAlchemy project, Python 3.11+ | `SQLAlchemy>=2.1` |
| Flask-SQLAlchemy 3.1.x in the project | `"SQLAlchemy<2.1"` (Flask-SQLAlchemy cannot build a `MappedAsDataclass` base on 2.1, [issue #1420](https://github.com/pallets-eco/flask-sqlalchemy/issues/1420); plain `db.Model` works, so the pin is a precaution) |
| Python 3.10 or older | `"SQLAlchemy<2.1"` (2.1 needs Python 3.11+) |

Then the rest of the dependency set:

| Package | Purpose | Required? |
|---------|---------|-----------|
| `SQLAlchemy` or `Flask-SQLAlchemy` | ORM | Yes |
| `alembic` or `Flask-Migrate` | Migrations | Recommended |
| Database driver | DB connection | Yes for PostgreSQL/MySQL |
| `sqlalchemy[asyncio]` | `greenlet` for the asyncio extension (not installed by default on 2.1) | Only for async code |

SQLite needs no driver; it is built into Python.

| Database | Driver package | URL prefix |
|----------|----------------|------------|
| PostgreSQL | `psycopg[binary]` | `postgresql+psycopg://` |
| PostgreSQL (async) | `psycopg[binary]` or `asyncpg` | `postgresql+psycopg://` or `postgresql+asyncpg://` |
| MySQL / MariaDB | `PyMySQL` | `mysql+pymysql://` |
| SQLite (async) | `aiosqlite` | `sqlite+aiosqlite://` |

Python: SQLAlchemy 2.0 runs on 3.7+, SQLAlchemy 2.1 needs 3.11+, Alembic 1.20 needs 3.10+. Details of what 2.1 changes: [SQLAlchemy 2.1](../api-reference/references/sqlalchemy-2.1.md).

### 2. Check Database URI

Verify the connection string format:

```python
# SQLite (file-based, relative to the working directory)
'sqlite:///app.db'
'sqlite:////absolute/path/to/database.db'
'sqlite://'  # In-memory (testing)

# PostgreSQL: name the driver (psycopg 3)
'postgresql+psycopg://user:password@host:5432/dbname'

# MySQL
'mysql+pymysql://user:password@host/dbname'
```

Always name the driver. A bare `postgresql://` URL means psycopg2 on SQLAlchemy 2.0 and psycopg 3 on 2.1, so the same file works on one version and raises `ModuleNotFoundError` on the other. `postgresql+psycopg://` behaves the same on both. `postgresql+psycopg2://` remains supported if you keep that driver on purpose.

In Flask-SQLAlchemy a relative SQLite path is resolved against the app's `instance` folder: `sqlite:///app.db` creates `instance/app.db`. Writing `sqlite:///instance/app.db` creates `instance/instance/app.db`.

Ensure the URI comes from environment variables, not hardcoded:

```python
# Good
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')

# Bad
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg://admin:secret@prod.example.com/mydb'
```

### 3. Check Initialization Pattern

For Flask-SQLAlchemy:
```python
# models.py: one Base, db created without an app
class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)

db = SQLAlchemy(model_class=Base)

# app.py: bind to the app in the factory
def create_app():
    app = Flask(__name__)
    db.init_app(app)
    return app
```

`db.create_all()` is not part of the factory: with Flask-Migrate or Alembic the schema comes from `flask db upgrade`. Keep `create_all()` for test fixtures and throwaway scripts.

For standalone SQLAlchemy:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(engine)

class Base(DeclarativeBase):
    pass
```

### 4. Check Model Definitions

Verify models have:
- Typed columns: `Mapped[...]` with `mapped_column()`, not bare `Column()`
- A primary key
- Proper column types and constraints
- Relationships declared with `back_populates` on both sides, and foreign keys indexed
- `__tablename__` set (required in plain SQLAlchemy; Flask-SQLAlchemy derives it from the class name when omitted)

### 5. Common Setup Issues

| Issue | Symptom | Fix |
|-------|---------|-----|
| No database file | `OperationalError: unable to open database` | Run `flask db upgrade` (or `alembic upgrade head`); `Base.metadata.create_all(engine)` only for tests and scripts |
| Driver not installed | `ModuleNotFoundError: No module named 'psycopg'` (or `'psycopg2'`) | Install the driver the URL names: `pip install "psycopg[binary]"` for `postgresql+psycopg://` |
| `postgresql://` URL after upgrading to 2.1 | `No module named 'psycopg'` although psycopg2 is installed | Use `postgresql+psycopg://` and install psycopg 3, or write `postgresql+psycopg2://` |
| Async engine fails to import | `ImportError: The SQLAlchemy asyncio module requires that the Python 'greenlet' library is installed` | `pip install "sqlalchemy[asyncio]"` |
| Missing app context | `RuntimeError: Working outside of application context` | Wrap in `with app.app_context():` |
| No migrations | Schema changes drop data | Install Flask-Migrate (or Alembic) and run `flask db init` |
| Models not imported | Migration or `create_all` sees no tables | Import every models module before reading `Base.metadata` |

## What This Skill Does NOT Cover

- Flask application structure (see flask-dev plugin)
- Deployment database setup (belongs in project template)
- Database server administration: roles, backups, tuning (outside this plugin)
