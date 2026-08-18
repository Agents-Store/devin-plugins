---
name: browser-sessions
description: Cloud browser sessions — create sessions, execute code, interact with dynamic pages. This skill should be used when the user needs to interact with SPAs, handle authentication flows, or execute browser automation on JavaScript-heavy sites.
---

# Cloud Browser Sessions

Cloud browser sessions let you programmatically interact with web pages — handle authentication, interact with SPAs, fill forms, and execute custom code.

## Tools

| Tool | Description |
|------|-------------|
| `browser_create` | Create a cloud browser session |
| `browser_execute` | Execute code in browser session |
| `browser_list` | List active browser sessions |
| `browser_delete` | Terminate a browser session |

## Create Browser Session

```
Tool: browser_create
Input: {
  "ttl": 300,
  "activityTtl": 60
}

Returns: { "sessionId": "session_xxx", "wsUrl": "wss://..." }
```

### Session Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `ttl` | number | Session time-to-live in seconds (30-3600) |
| `activityTtl` | number | Inactivity timeout in seconds (10-3600) |
| `streamWebView` | boolean | Enable web view streaming |
| `profile.name` | string | Browser profile name (for persistent sessions) |
| `profile.saveChanges` | boolean | Save profile changes |

## Execute Code in Browser

```
Tool: browser_execute
Input: {
  "sessionId": "session_xxx",
  "code": "await page.goto('https://example.com'); return await page.title();",
  "language": "javascript"
}

Returns: { "result": "Example Domain" }
```

### Supported Languages

| Language | Use Case |
|----------|----------|
| `javascript` | Page interaction, DOM manipulation, Playwright-style automation |
| `python` | Data processing, complex logic |
| `bash` | System commands, file operations |

## List Browser Sessions

```
Tool: browser_list
Input: { "status": "active" }

Returns: [
  { "sessionId": "session_xxx", "status": "active", "createdAt": "..." }
]
```

## Delete Browser Session

```
Tool: browser_delete
Input: { "sessionId": "session_xxx" }

Returns: { "success": true }
```

## Workflows

### Interact with Dynamic Page
```
1. browser_create(ttl=300) → Create session
2. browser_execute(sessionId, code="
     await page.goto('https://app.example.com/login');
     await page.fill('#email', 'user@example.com');
     await page.fill('#password', 'pass');
     await page.click('#submit');
     await page.waitForNavigation();
     return await page.content();
   ", language="javascript") → Login and get content
3. browser_execute(sessionId, code="
     await page.goto('https://app.example.com/dashboard');
     return await page.textContent('.stats');
   ", language="javascript") → Navigate and extract data
4. browser_delete(sessionId) → Clean up
```

### Scrape Behind Authentication
```
1. browser_create(ttl=600) → Create session
2. browser_execute → Login to site
3. browser_execute → Navigate to protected pages
4. browser_execute → Extract data from each page
5. browser_delete → Clean up session
```

## Best Practices

1. **Always clean up** — delete sessions when done
2. **Set appropriate TTL** — don't waste resources on idle sessions
3. **Use JavaScript for page interaction** — Playwright-style API
4. **Handle errors in code** — wrap in try/catch
5. **Check session list** — verify active sessions before creating new ones

## Error Handling

- **Session expired** → create a new session with longer TTL
- **Code execution fails** → check for typos, ensure page has loaded before interacting
- **Login fails** → verify selectors (#email, #submit) match the actual page
- **Session leak** → always list sessions and delete unused ones
