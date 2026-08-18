---
name: model-patterns
description: >
  Use when the user asks about "SQLAlchemy models", "define database model",
  "SQLAlchemy relationships", "one-to-many relationship", "many-to-many",
  "SQLAlchemy column types", "model constraints", "Flask-SQLAlchemy model",
  or needs patterns for defining database models with SQLAlchemy.
---

# SQLAlchemy Model Patterns

Production patterns for defining models, relationships, and constraints with SQLAlchemy 2.0+.

## Flask-SQLAlchemy Model Definition

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    posts = db.relationship('Post', backref='author', lazy=True)
```

## Standalone SQLAlchemy 2.0 (Mapped Annotations)

```python
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True)

    posts: Mapped[list["Post"]] = relationship(back_populates="author")
```

## Column Types

| Python Type | SQLAlchemy Type | Use Case |
|-------------|----------------|----------|
| `int` | `Integer` | IDs, counts |
| `str` | `String(N)` | Short text (name, email) |
| `str` | `Text` | Long text (notes, content) |
| `bool` | `Boolean` | Flags |
| `float` | `Float` | Approximate numbers |
| `Decimal` | `Numeric(10, 2)` | Exact numbers (money) |
| `date` | `Date` | Date only |
| `time` | `Time` | Time only |
| `datetime` | `DateTime` | Date + time |
| `bytes` | `LargeBinary` | Binary data |

## Constraints

```python
# Unique constraint
email = db.Column(db.String(120), unique=True)

# Not null
name = db.Column(db.String(100), nullable=False)

# Default value
status = db.Column(db.String(20), default='new')

# Dynamic default (use lambda for mutable defaults)
created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# Check constraint
age = db.Column(db.Integer, db.CheckConstraint('age >= 0'))

# Composite unique constraint
__table_args__ = (db.UniqueConstraint('user_id', 'date', 'procedure'),)

# Index
__table_args__ = (db.Index('idx_user_date', 'user_id', 'date'),)
```

## Relationships

### One-to-Many

```python
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    clients = db.relationship('Client', backref='user', lazy=True)

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
```

### One-to-Many with Cascade Delete

```python
class Client(db.Model):
    appointments = db.relationship(
        'Appointment', backref='client', lazy=True,
        cascade='all, delete-orphan'
    )
```

When the client is deleted, all their appointments are automatically deleted.

### Many-to-Many

```python
# Association table
tags_posts = db.Table('tags_posts',
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'))
)

class Post(db.Model):
    tags = db.relationship('Tag', secondary=tags_posts, backref='posts')
```

### Self-Referential (Hierarchical)

```python
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))
```

## Computed Properties

Use `@property` for values derived from other tables:

```python
class Client(db.Model):
    @property
    def visit_count(self):
        return Appointment.query.filter_by(
            client_id=self.id, status='done'
        ).count()
```

## Model Mixins

Share common columns across models:

```python
class TimestampMixin:
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate=lambda: datetime.now(timezone.utc))

class User(TimestampMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    # inherits created_at and updated_at
```

## Enum Columns

```python
import enum

class StatusEnum(enum.Enum):
    NEW = 'new'
    REGULAR = 'regular'
    VIP = 'vip'

class Client(db.Model):
    status = db.Column(db.Enum(StatusEnum), default=StatusEnum.NEW)
```

Or use string-based approach for simpler cases:

```python
status = db.Column(db.String(20), default='new')  # new/regular/vip
```
