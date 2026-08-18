---
name: api-reference
description: >
  Use when the user asks for "SQLAlchemy API reference", "SQLAlchemy Column types",
  "SQLAlchemy session methods", "db.session API", "SQLAlchemy relationship options",
  or needs specific SQLAlchemy framework API details.
disable-model-invocation: true
---

# SQLAlchemy API Reference

Curated SQLAlchemy 2.0+ API. For full docs, see https://docs.sqlalchemy.org/

## Column Types

```python
db.Column(db.Integer)            # int
db.Column(db.String(N))          # varchar(N)
db.Column(db.Text)               # text (unlimited)
db.Column(db.Boolean)            # boolean
db.Column(db.Float)              # float
db.Column(db.Numeric(10, 2))     # decimal (exact)
db.Column(db.Date)               # date
db.Column(db.Time)               # time
db.Column(db.DateTime)           # datetime
db.Column(db.LargeBinary)        # blob
db.Column(db.JSON)               # json (PostgreSQL/MySQL)
db.Column(db.Enum('a', 'b'))     # enum
```

## Column Options

```python
db.Column(db.Integer, primary_key=True)
db.Column(db.String(100), nullable=False)      # NOT NULL
db.Column(db.String(120), unique=True)          # UNIQUE
db.Column(db.String(20), default='new')         # Default value
db.Column(db.DateTime, default=func.now())      # Server default
db.Column(db.Integer, index=True)               # Create index
db.Column(db.Integer, db.ForeignKey('table.id')) # Foreign key
```

## Session Methods

```python
db.session.add(obj)              # Stage new object for INSERT
db.session.add_all([a, b, c])    # Stage multiple objects
db.session.delete(obj)           # Stage for DELETE
db.session.commit()              # Flush and commit transaction
db.session.rollback()            # Rollback current transaction
db.session.flush()               # Flush without commit
db.session.get(Model, pk)        # Get by primary key (2.0)
db.session.execute(stmt)         # Execute a select/insert/update
db.session.merge(obj)            # Merge detached object
db.session.refresh(obj)          # Reload from DB
db.session.expunge(obj)          # Remove from session
```

## Relationship Options

```python
db.relationship('Model',
    backref='parent',              # Reverse reference name
    back_populates='children',     # Explicit bidirectional
    lazy=True,                     # Load strategy: True/select/joined/subquery/selectin
    cascade='all, delete-orphan',  # Delete children when parent deleted
    uselist=False,                 # One-to-one (instead of one-to-many)
    order_by='Model.name',         # Default ordering
    foreign_keys=[Model.parent_id], # Explicit FK (for self-ref)
    secondary=association_table,    # Many-to-many junction table
)
```

## Query Methods (Flask-SQLAlchemy)

```python
Model.query.all()                    # All records
Model.query.first()                  # First or None
Model.query.get_or_404(id)           # Get or abort(404)
Model.query.filter_by(k=v)          # Filter by keyword args
Model.query.filter(Model.k == v)    # Filter by expression
Model.query.order_by(Model.k.desc()) # Order results
Model.query.limit(10)               # Limit results
Model.query.offset(20)              # Skip results
Model.query.count()                 # Count matching
Model.query.paginate(page=1, per_page=20)  # Paginate
Model.query.with_entities(Model.name)       # Select specific columns
```

## Aggregate Functions

```python
from sqlalchemy import func
func.count(Model.id)   func.sum(Model.amount)   func.avg(Model.price)
func.min(Model.date)   func.max(Model.date)
```

For Alembic migration API, async, and advanced patterns, see `references/advanced-api.md`.
