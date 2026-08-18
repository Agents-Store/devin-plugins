---
name: setup
description: >
  Use when the user asks to "verify SQLAlchemy setup", "check database connection",
  "is SQLAlchemy configured correctly", "test database setup", or needs to confirm
  that SQLAlchemy is properly initialized in their Python project.
---

# SQLAlchemy Setup Verification

Verify that SQLAlchemy is correctly configured and the database connection works.

## Verification Steps

### 1. Check Dependencies

Read `requirements.txt` or `pyproject.toml` and verify:

| Package | Purpose | Required? |
|---------|---------|-----------|
| `SQLAlchemy` or `Flask-SQLAlchemy` | ORM | Yes |
| `alembic` or `Flask-Migrate` | Migrations | Recommended |
| Database driver (`psycopg2`, `pymysql`, etc.) | DB connection | Yes for PostgreSQL/MySQL |

SQLite needs no driver — it's built into Python.

### 2. Check Database URI

Verify the connection string format:

```python
# SQLite (file-based)
'sqlite:///instance/app.db'
'sqlite:///path/to/database.db'
'sqlite:///:memory:'  # In-memory (testing)

# PostgreSQL
'postgresql://user:password@host:5432/dbname'
'postgresql+psycopg2://user:password@host/dbname'

# MySQL
'mysql+pymysql://user:password@host/dbname'
```

Ensure the URI comes from environment variables, not hardcoded:

```python
# Good
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')

# Bad
SQLALCHEMY_DATABASE_URI = 'postgresql://admin:secret@prod.example.com/mydb'
```

### 3. Check Initialization Pattern

For Flask-SQLAlchemy:
```python
# models.py — create db instance
db = SQLAlchemy()

# app.py — bind to app in factory
def create_app():
    app = Flask(__name__)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return app
```

For standalone SQLAlchemy:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass
```

### 4. Check Model Definitions

Verify models have:
- Primary key defined
- Proper column types and constraints
- Relationships with correct foreign keys
- `__tablename__` set explicitly

### 5. Common Setup Issues

| Issue | Symptom | Fix |
|-------|---------|-----|
| No database file | `OperationalError: unable to open database` | Run `db.create_all()` or `flask db upgrade` |
| Wrong driver | `ModuleNotFoundError: No module named 'psycopg2'` | Install the database driver package |
| No `SQLALCHEMY_TRACK_MODIFICATIONS` | Deprecation warning | Set `app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False` |
| Missing app context | `RuntimeError: Working outside of application context` | Wrap in `with app.app_context():` |
| No migrations | Schema changes drop data | Install Flask-Migrate and run `flask db init` |

## What This Skill Does NOT Cover

- Flask application structure (see flask-dev plugin)
- Deployment database setup (belongs in project template)
- Database administration (see postgresql-provision plugin)
