# Feature: {{FEATURE_NAME}}

## Step 1: Data Model
- Table name: `{{table_name}}`
- Columns: id, user_id, {{columns}}
- Relationships: {{relationships}}
- Migration: `flask db migrate -m "Add {{table_name}} table"` → `flask db upgrade`

## Step 2: Blueprint
- File: `routes/{{feature}}.py`
- Blueprint name: `{{feature}}_bp`
- Register in `create_app()`

## Step 3: Routes
- `GET /{{feature}}` — List all (filtered by `current_user.id`)
- `POST /{{feature}}/add` — Create new
- `POST /{{feature}}/edit/<id>` — Update existing
- `POST /{{feature}}/delete/<id>` — Delete with confirmation
- All routes decorated with `@login_required`

## Step 4: Template
- File: `templates/{{feature}}.html`
- Extends `base.html`
- Blocks: title, extra_css, content
- Components: list view, add form, edit modal, delete confirmation

## Step 5: Styles
- File: `static/css/{{feature}}.css`
- Follow existing design tokens from `base.css`

## Step 6: Navigation
- Add link in `base.html` nav with active state detection

## Step 7: Verify
- [ ] CRUD operations work
- [ ] Data isolated per user
- [ ] Flash messages display correctly
- [ ] Form validation works
- [ ] Page matches existing app style
