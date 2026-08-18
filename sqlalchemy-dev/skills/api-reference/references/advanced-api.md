# SQLAlchemy Advanced API Reference

## Alembic Migration API

```bash
# Flask-Migrate commands
flask db init                         # Initialize migrations (once)
flask db migrate -m "Description"     # Auto-generate migration
flask db upgrade                      # Apply all pending migrations
flask db downgrade                    # Revert last migration
flask db current                      # Show current revision
flask db history                      # Show migration history
flask db stamp head                   # Mark DB as up-to-date without running
```

```bash
# Standalone Alembic commands
alembic init alembic                  # Initialize
alembic revision --autogenerate -m "msg"  # Generate migration
alembic upgrade head                  # Apply all
alembic downgrade -1                  # Revert one
alembic current                       # Current revision
alembic history                       # History
```

## Table Arguments

```python
class MyModel(db.Model):
    __tablename__ = 'my_model'
    __table_args__ = (
        db.UniqueConstraint('col_a', 'col_b', name='uq_a_b'),
        db.Index('idx_col_a', 'col_a'),
        db.CheckConstraint('price >= 0', name='ck_positive_price'),
        {'schema': 'myschema'},  # dict must be last
    )
```

## Hybrid Properties

```python
from sqlalchemy.ext.hybrid import hybrid_property

class User(db.Model):
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))

    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @full_name.expression
    def full_name(cls):
        return cls.first_name + ' ' + cls.last_name
```

## Events

```python
from sqlalchemy import event

@event.listens_for(User, 'before_insert')
def set_defaults(mapper, connection, target):
    if not target.status:
        target.status = 'new'

@event.listens_for(db.session, 'after_commit')
def after_commit(session):
    # Post-commit logic
    pass
```

## Async SQLAlchemy

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

engine = create_async_engine('postgresql+asyncpg://user:pass@host/db')
async_session = async_sessionmaker(engine, class_=AsyncSession)

async def get_users():
    async with async_session() as session:
        result = await session.execute(select(User))
        return result.scalars().all()
```

## Batch Operations

```python
# Bulk insert (faster than add_all for large datasets)
db.session.execute(
    User.__table__.insert(),
    [{'name': 'A', 'email': 'a@example.com'}, {'name': 'B', 'email': 'b@example.com'}]
)
db.session.commit()

# Bulk update
db.session.execute(
    User.__table__.update().where(User.status == 'new').values(status='active')
)
db.session.commit()
```
