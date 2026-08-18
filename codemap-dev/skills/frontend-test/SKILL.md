---
name: frontend-test
description: >
  This skill should be used when the user asks to "test the frontend", "check the UI", "explore the app in a browser",
  "test my admin panel", "find frontend bugs", "check for console errors", "verify the app works in a browser",
  "test user flows", "check the website", or wants a comprehensive frontend health report for a running application.
  Also triggers when the user says "open my app and test it", "browse my app", "check if the UI is working",
  or "give me a frontend report". Uses Playwright MCP to navigate, interact, and diagnose.
---

# Frontend Testing via Playwright MCP

## Step 0: Execution Mode (MANDATORY)

Before doing ANY work, ask the user:

> "Want me to delegate this to the **frontend-tester** agent (isolated, structured testing), or proceed inline in this chat?"

- If user chooses agent → launch the **frontend-tester** agent with the target URL and context. STOP here — do not continue with the steps below.
- If user chooses inline → proceed with the methodology below.
- If user doesn't respond clearly → default to agent.

---

Test a running application's frontend by navigating pages, interacting with UI elements, collecting errors, and generating a structured health report. All browser interaction happens via Playwright MCP tools — no manual browser needed.

## Prerequisites

- The application must be running and accessible (localhost or remote URL)
- Playwright MCP server must be connected (check with `/mcp`)
- If the app requires authentication, ask the user for credentials before starting

## Step 1: Determine Target URL

Resolve the application URL in this order:

1. **User provided URL** — use it directly (add `http://` if missing)
2. **Detect from project** — check `package.json` scripts for dev server port, `docker-compose.yml` for exposed ports, `.env` for `PORT` or `BASE_URL` variables
3. **Ask the user** — if nothing is detectable, ask for the URL

Common patterns:
- Next.js / React: `http://localhost:3000`
- Flask / Django: `http://localhost:5000` or `http://localhost:8000`
- Docker Compose: check `ports` mapping in `docker-compose.yml`
- Admin panels: often at `/admin`, `/dashboard`, `/panel`

## Step 2: Discovery Phase

Navigate to the app and map its structure.

### 2a. Initial Page Load

1. Use `browser_navigate` to open the target URL
2. Use `browser_snapshot` to get the accessibility tree of the landing page
3. Use `browser_console_messages` to check for immediate JavaScript errors
4. Use `browser_network_requests` to check for failed resource loads (4xx/5xx)

### 2b. Navigation Mapping

From the accessibility tree, identify:
- **Top-level navigation** — menus, navbars, sidebars, header links
- **Page links** — all internal links discoverable from the current page
- **Authentication state** — is the user logged in? Is there a login page?
- **Key sections** — main content areas, footers, modals

Build a page list by extracting links from the snapshot. Visit up to **10 unique pages** (prioritize distinct routes, not paginated variants).

### 2c. Page-by-Page Scan

For each discovered page:

1. `browser_navigate` to the page URL
2. `browser_snapshot` to capture the accessibility tree
3. `browser_console_messages` to collect JS errors/warnings
4. `browser_network_requests` to check for failed API calls
5. Note the page title, main content structure, and any interactive elements (forms, buttons, tables)

Record findings per page:
- **URL and title**
- **Key elements** (forms, tables, lists, buttons, media)
- **Console errors** (if any)
- **Failed network requests** (if any)

## Step 3: Interaction Testing

Test the interactive elements discovered during the scan.

### 3a. Form Testing

For each form found:

1. Identify form fields via `browser_snapshot` (inputs, selects, textareas, checkboxes)
2. Test empty submission — `browser_click` the submit button without filling fields. Check for validation messages
3. Test with valid data — `browser_fill_form` or `browser_type` to fill fields, then submit. Check for success/error responses
4. Check field types — do email fields validate email format? Do required fields show errors?

**Do NOT submit forms that create real data in production.** If unsure whether the app is a development instance, ask the user before submitting forms.

### 3b. Navigation Testing

1. Click through the main navigation items using `browser_click`
2. Verify each link leads to the expected page (check URL and page title)
3. Test the browser back button with `browser_navigate_back`
4. Check for broken links (pages that return errors or show empty content)

### 3c. Interactive Elements

1. Test buttons — do they trigger expected actions (modals, toggles, expandable sections)?
2. Test dropdowns — do `browser_select_option` calls work? Do options load?
3. Test search — if a search bar exists, `browser_type` a query and check results
4. Test modals/dialogs — can they be opened and closed? Do `browser_handle_dialog` calls work?

## Step 4: Error Analysis

Compile all errors collected during Steps 2 and 3.

### 4a. Console Errors

Categorize console messages:
- **Errors** (red) — JavaScript exceptions, failed assertions, uncaught promises
- **Warnings** (yellow) — deprecation notices, React warnings, CSP violations
- **Info** — development messages (usually ignorable)

Focus on errors. Group by type (e.g., "TypeError: Cannot read property X" across 3 pages).

### 4b. Network Failures

Categorize failed requests:
- **4xx errors** — missing API endpoints, unauthorized access, not found resources
- **5xx errors** — server crashes, timeouts, internal errors
- **CORS issues** — blocked cross-origin requests
- **Missing resources** — 404 for images, scripts, stylesheets, fonts

### 4c. UI Issues

Note any structural problems detected from accessibility snapshots:
- Empty pages or sections with no content
- Missing labels on form fields (accessibility issue)
- Broken layouts (elements with unusual positioning inferred from tree structure)
- Missing alt text on images
- Non-functional buttons or links

## Step 5: Generate Report

Create the report at `docs/codemap/FRONTEND.md`.

### Report Structure

```markdown
# Frontend Report — {App Name}

**URL:** {base URL}
**Tested:** {date}
**Pages scanned:** {count}

## Summary

{2-3 sentence overview: how many pages found, how many errors, overall health assessment}

| Metric | Count |
|--------|-------|
| Pages scanned | X |
| Console errors | X |
| Console warnings | X |
| Failed network requests | X |
| Forms tested | X |
| Broken links | X |

## Pages Discovered

| # | URL | Title | Status |
|---|-----|-------|--------|
| 1 | /   | Home  | OK / Issues found |
| 2 | /about | About | OK |
| ... | ... | ... | ... |

## Console Errors

### {Error type/message}
- **Pages affected:** {list of URLs}
- **Frequency:** {count}
- **Impact:** {what functionality is affected}

## Network Failures

### {Endpoint or resource}
- **Status:** {HTTP status code}
- **Pages affected:** {list of URLs}
- **Impact:** {what breaks — missing data, broken images, etc.}

## Forms

### {Form name/location}
- **URL:** {page URL}
- **Fields:** {count and types}
- **Validation:** {works / missing / broken}
- **Submission:** {tested / skipped — reason}

## UI Issues

### {Issue description}
- **URL:** {page URL}
- **Element:** {what element is affected}
- **Impact:** {accessibility, usability, visual}

## Recommendations

1. {Highest priority fix — with specific location and suggested action}
2. {Next priority}
3. {Next priority}
```

### Report Rules

- Use real URLs, page titles, and error messages from the test — no generic placeholders
- Group similar errors (e.g., same TypeError across pages) instead of listing each individually
- Prioritize recommendations by impact: data-loss risks first, then broken features, then UI polish
- If everything is working well, say so — don't invent issues
- Include the date of the test so the report can be compared with future runs
- Create `docs/codemap/` directory if it doesn't exist

## Error Handling

### App not reachable
If `browser_navigate` fails with a connection error:
> "Cannot reach {URL}. Make sure the application is running. Check with `npm run dev`, `docker compose ps`, or the relevant start command for your project."

### Authentication required
If the landing page is a login screen:
1. Ask the user for credentials (username/password or login method)
2. Use `browser_fill_form` or `browser_type` to log in
3. After login, proceed with the discovery phase from the authenticated state
4. Note in the report that testing was done in authenticated mode

### Playwright MCP not connected
If Playwright MCP tools are unavailable:
> "Playwright MCP server is not connected. Run `/mcp` to check server status. The plugin expects a `playwright` MCP server configured in `.mcp.json`."

### Dynamic content / SPAs
For single-page applications where content loads asynchronously:
- Use `browser_wait_for` after navigation to wait for key content to appear
- Check `browser_network_requests` for pending API calls before taking snapshots
- Retry snapshot if the page appears empty on first capture
