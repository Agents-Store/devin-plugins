# Domain Analytics Tools

4 tools for technology detection and WHOIS data. All prefixed with `mcp__dataforseo__`.

## Tool Reference

### Technology Detection

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `domain_analytics_technologies_domain_technologies` | Detect technologies used by a domain | `target` (domain, required) |
| `domain_analytics_technologies_available_filters` | List available technology filter options | `tool` (optional) |

### WHOIS

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `domain_analytics_whois_overview` | Search WHOIS records with filters | `filters`, `limit`, `offset`, `order_by` |
| `domain_analytics_whois_available_filters` | List available WHOIS filter options | `tool` (optional) |

## Parameter Details

### domain_analytics_technologies_domain_technologies

- `target` -- the domain to analyze. Example: `"example.com"`. Do not include protocol or path.
- Returns a comprehensive list of technologies detected on the domain: CMS, frameworks, analytics tools, CDNs, hosting, JavaScript libraries, advertising platforms, and more.

### domain_analytics_technologies_available_filters

- `tool` -- optional. Pass a specific tool name to get filters for that tool only.
- Returns the list of available filter fields and operators. Call this first if you plan to use technology-based filtering.

### domain_analytics_whois_overview

- `filters` -- array syntax: `[["registrar", "=", "GoDaddy.com, LLC"]]` or `[["expiration_datetime", "<", "2026-01-01"]]`.
- `limit` -- max results. Default 10, max 1000.
- `offset` -- pagination offset.
- `order_by` -- array: `["creation_datetime,desc"]`.
- Searchable fields include: `domain`, `registrar`, `creation_datetime`, `expiration_datetime`, `updated_datetime`, `registrant_name`, `registrant_organization`, `registrant_country`.

### domain_analytics_whois_available_filters

- Returns the full list of WHOIS filter fields and operators. Consult this before constructing complex WHOIS queries.

## Usage Examples

### Check a competitor's tech stack

```
Tool: mcp__dataforseo__domain_analytics_technologies_domain_technologies
Params:
  target: "competitor.com"
```

Returns detected technologies grouped by category (e.g., CMS: WordPress, Analytics: Google Analytics 4, CDN: Cloudflare, Framework: React). Useful for understanding competitor infrastructure and identifying tools they use.

### Find domains expiring soon

```
Tool: mcp__dataforseo__domain_analytics_whois_overview
Params:
  filters: [["expiration_datetime", "<", "2026-06-01"], "and", ["registrant_country", "=", "US"]]
  limit: 50
  order_by: ["expiration_datetime,asc"]
```

Returns domains registered in the US that expire before the specified date. Useful for domain acquisition opportunities.

## Tips

- Technology detection works on the live site. If a domain is down, the tool may return incomplete results.
- WHOIS data availability varies by registrar and privacy settings. Some domains have redacted WHOIS info.
- Use `available_filters` tools to discover valid filter fields before writing complex queries.
- Technology detection is useful for competitive analysis, lead generation (find sites using a specific CMS), and security audits.
- WHOIS queries are powerful for bulk domain research -- find domains by registrar, country, or expiration window.
