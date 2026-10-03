# Feature: {{FEATURE_NAME}}

## Step 1: Data Model
- Table name: `{{table_name}}`
- Class: `{{Model}}(OwnedMixin, db.Model)`, typed columns (`Mapped[...]`, `mapped_column(...)`): id, user_id (from `OwnedMixin`), {{columns}}
- Relationships: {{relationships}} (`back_populates` on both sides, `lazy='raise'` on collections and many-to-one)
- Migration: `flask db migrate -m "Add {{table_name}} table"`, then read the revision (it must contain your change), `flask db upgrade`, `flask db check`

## Step 2: Blueprint
- File: `routes/{{feature}}.py`
- Blueprint name: `{{feature}}_bp`
- Register in `create_app()`

## Step 3: Routes
- `GET /{{feature}}` — list, starting from `owned_by({{Model}}, current_user.id)`, with the loaders the template needs
- `POST /{{feature}}/add` — create (a foreign key from the form is fetched through `owned_by` first)
- `POST /{{feature}}/<int:id>/edit` — update (`db.one_or_404(owned_by(...).where(...))`)
- `POST /{{feature}}/<int:id>/delete` — delete
- All routes decorated with `@login_required`; every write: one `commit()`, then a redirect

## Step 4: Template
- File: `templates/{{feature}}.html`
- Extends `base.html`
- Blocks: title, extra_css, content
- Components: list view, add form, edit modal, delete confirmation; every `POST` form has `csrf_token`

## Step 5: Styles
- File: `static/css/{{feature}}.css`
- Follow existing design tokens from `base.css`

## Step 6: Navigation
- Add link in `base.html` nav with active state detection

## Step 7: Verify
- [ ] CRUD operations work
- [ ] Another user gets 404 for these ids (edit, delete)
- [ ] The list view issues the same number of statements for few and for many rows
- [ ] Writes are committed (assert in a fresh `with app.app_context():` after the request)
- [ ] Flash messages display correctly
- [ ] Form validation works
- [ ] `flask db check` is clean
- [ ] Page matches existing app style
