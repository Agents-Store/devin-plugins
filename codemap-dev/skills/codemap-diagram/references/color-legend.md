# Color Legend for Codemap Diagrams

All diagrams must use consistent colors to help beginners quickly identify component types across different diagrams.

## Color Assignments

| Layer | Fill Color | Border Color | Hex Fill | Hex Border | Use For |
|-------|-----------|-------------|----------|------------|---------|
| Data | Light Blue | Blue | `#dae8fc` | `#6c8ebf` | Database tables, models, migrations, ORM queries, data files |
| Logic | Light Green | Green | `#d5e8d4` | `#82b366` | Route handlers, services, business logic, controllers, middleware |
| Interface | Light Yellow | Orange | `#fff2cc` | `#d6b656` | Templates, HTML, static files, API endpoints, forms, CLI commands |
| External | Light Red | Red | `#f8cecc` | `#b85450` | Third-party APIs, MCP servers, external services, webhooks |
| Auth | Light Purple | Purple | `#e1d5e7` | `#9673a6` | Login, registration, session management, permissions, tokens |
| Infra | Light Gray | Dark Gray | `#f5f5f5` | `#666666` | Docker, config files, CI/CD, environment variables, deployment |

## mxGraph Style Strings

Use these in the `style` attribute of mxCell elements:

```
Data:      rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;
Logic:     rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;
Interface: rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;
External:  rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;
Auth:      rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;
Infra:     rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;
```

## Edge Styles

```
Default edge:   edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;
FK relationship: edgeStyle=entityRelationEdgeStyle;strokeColor=#6c8ebf;
Error path:     strokeColor=#b85450;dashed=1;
```

## Text Styles

```
Title:     text;html=1;fontSize=16;fontStyle=1;align=center;
Label:     text;html=1;fontSize=11;align=center;
Note:      text;html=1;fontSize=10;fontStyle=2;fillColor=#ffffcc;strokeColor=#cccc00;
```

## Usage Rules

1. **Always include a color legend** in architecture and ERD diagrams (small box in corner)
2. **Be consistent** — if User model is blue in the ERD, it must be blue in the sequence diagram too
3. **Use border color for edges** connecting to that layer (e.g., blue edges for database relationships)
4. **White text on dark fills** — if you ever use a dark fill, switch to white text for readability
5. **One primary color per node** — don't mix colors. If a component spans layers, use the dominant layer's color