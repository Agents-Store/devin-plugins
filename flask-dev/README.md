# flask-dev (Devin plugin)

Flask dev plugin for Agents Store. Application factory patterns, blueprint organization, Jinja2 templates, Flask CLI recipes, and troubleshooting for developers building with Flask.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (6)

- `api-reference` — Use when the user asks for "Flask API reference", "Flask decorators", "Flask request object", "Flask response", "Flask config options", "Flask url_for", "Flask flash messages", or needs specific Flask framework API details.

- `app-patterns` — Use when the user asks about "Flask application factory", "Flask blueprints", "Flask config management", "Flask extensions", "organize Flask project", "Flask app structure", "register Flask blueprint", "Flask context processors", or needs patterns for structuring a Flask application.

- `cli-recipes` — Use when the user asks about "Flask CLI", "flask run", "flask shell", "flask routes", "Flask command line", "custom Flask CLI command", "run Flask from terminal", or needs ready-to-use Flask CLI commands.

- `jinja2-patterns` — Use when the user asks about "Jinja2 templates", "Flask templates", "template inheritance", "Jinja2 macros", "Jinja2 filters", "Flask render_template", "base template", "template blocks", or needs patterns for Jinja2 template engine in Flask.

- `setup` — Use when the user asks to "verify Flask project setup", "check Flask structure", "is my Flask app set up correctly", "validate Flask project", or needs to confirm that a Flask project follows recommended patterns and has correct file structure.

- `troubleshoot` — Use when the user encounters "Flask errors", "Flask not working", "Flask import error", "Flask 500 error", "debug Flask", "Flask template not found", "Flask circular import", or needs to diagnose and fix common Flask problems.


## Not carried over

- 1 agent(s) — Devin plugins do not support agents

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/flask-dev
