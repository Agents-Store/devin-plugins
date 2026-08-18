---
name: cli-recipes
description: >
  Use when the user asks about "Alembic commands", "database migrations",
  "flask db migrate", "flask db upgrade", "create migration",
  "rollback migration", "SQLAlchemy CLI", or needs ready-to-use
  database migration commands.
---

# Alembic / Flask-Migrate CLI Recipes

Ready-to-use commands for database schema migrations.

## Flask-Migrate (Flask Projects)

### Initial Setup

```bash
pip install Flask-Migrate
```

```python
# In app.py
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    db.init_app(app)
    Migrate(app, db)  # Add this line
    return app
```

```bash
# Initialize migrations directory (run once)
flask db init
```

### Migration Workflow

```bash
# 1. Make model changes in models.py
# 2. Generate migration script
flask db migrate -m "Add phone column to clients"

# 3. Review the generated migration in migrations/versions/
# 4. Apply migration
flask db upgrade

# Verify current state
flask db current
```

### Common Operations

```bash
# Apply all pending migrations
flask db upgrade

# Rollback last migration
flask db downgrade

# Show migration history
flask db history

# Show current revision
flask db current

# Mark DB as current without running migrations
flask db stamp head

# Generate empty migration (for manual edits)
flask db revision -m "Custom migration"
```

## Standalone Alembic

### Initial Setup

```bash
pip install alembic
alembic init alembic
```

Edit `alembic/env.py` to point to your models and database URL.

### Migration Workflow

```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "Add phone column"

# Apply all pending
alembic upgrade head

# Rollback one step
alembic downgrade -1

# Rollback to specific revision
alembic downgrade abc123

# View history
alembic history

# Current revision
alembic current
```

## Manual Migration Edits

Sometimes autogenerate misses changes. Edit the migration file directly:

```python
# In migrations/versions/xxxx_add_phone_column.py
def upgrade():
    op.add_column('clients', sa.Column('phone', sa.String(20), nullable=True))
    op.create_index('idx_clients_phone', 'clients', ['phone'])

def downgrade():
    op.drop_index('idx_clients_phone', 'clients')
    op.drop_column('clients', 'phone')
```

### Common Migration Operations

```python
from alembic import op
import sqlalchemy as sa

# Add column
op.add_column('table', sa.Column('col', sa.String(100)))

# Drop column
op.drop_column('table', 'col')

# Rename column
op.alter_column('table', 'old_name', new_column_name='new_name')

# Change column type
op.alter_column('table', 'col', type_=sa.Text())

# Add index
op.create_index('idx_name', 'table', ['col'])

# Add unique constraint
op.create_unique_constraint('uq_name', 'table', ['col'])

# Add foreign key
op.create_foreign_key('fk_name', 'child', 'parent', ['parent_id'], ['id'])

# Create table
op.create_table('new_table',
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(100)),
)

# Drop table
op.drop_table('old_table')
```

## Troubleshooting Migrations

| Issue | Fix |
|-------|-----|
| "Target database is not up to date" | Run `flask db upgrade` first |
| "Can't locate revision" | Run `flask db stamp head` to reset |
| Autogenerate misses changes | Edit migration manually |
| Migration fails midway | Fix the migration, then `flask db upgrade` again |
| Need to start fresh | Delete `migrations/`, run `flask db init` + `flask db migrate` |
