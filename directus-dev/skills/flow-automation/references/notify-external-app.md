# Notify an External App from a Flow (Cache Revalidation)

A Flow that calls your frontend when content changes, so the site refreshes without a rebuild. The same shape serves any outgoing webhook. Checked on Directus 12.4.1 with a throwaway instance: the receiver got the POST with the secret header and the JSON body.

## The flow

An event trigger (`action`, so it runs after the change is committed) and one `request` operation:

```json
{
  "name": "Revalidate frontend",
  "status": "active",
  "trigger": "event",
  "accountability": "all",
  "options": {
    "type": "action",
    "scope": ["items.create", "items.update", "items.delete"],
    "collections": ["posts", "authors", "categories"]
  }
}
```

```json
{
  "name": "Call frontend",
  "key": "call_frontend",
  "type": "request",
  "options": {
    "method": "POST",
    "url": "https://app.example.com/api/revalidate",
    "headers": [
      { "header": "Content-Type", "value": "application/json" },
      { "header": "x-revalidate-secret", "value": "{{ $env.REVALIDATION_SECRET }}" }
    ],
    "body": "{\"collection\":\"{{ $trigger.collection }}\"}"
  }
}
```

Do not add a condition such as `status == published`: an edit that unpublishes or archives an item has to refresh the site as well, or the old page stays up. Let the receiving side decide what to do with the collection name.

Create the flow, then the operation with that `flow` id, then PATCH the flow's `operation` to the operation id (see "Creating Operations" in `SKILL.md`). The receiver gets `{"collection":"posts"}` and decides which cache tags to invalidate (see `nextjs-dev`, `data-fetching`).

## The secret goes in a header, and `$env` needs an allow-list

- A secret in the query string (`?secret=...`) ends up in access logs of the receiver and of every proxy on the way. Send it in a header.
- Flows cannot read environment variables by default. List the names you want in `FLOWS_ENV_ALLOW_LIST` on the Directus container, together with the variable itself:

```yaml
environment:
  REVALIDATION_SECRET: ${REVALIDATION_SECRET}
  FLOWS_ENV_ALLOW_LIST: REVALIDATION_SECRET
```

`{{ $env.REVALIDATION_SECRET }}` then resolves inside operation options (verified). Without the allow-list nothing warns you: the template renders the literal text `undefined` and the request goes out with `undefined` as the secret, so the receiver answers `401`. Any variable on that list is readable by every flow author, so list only values you are willing to show them. Do not paste the secret into the operation: the value would live in the database and in schema snapshots.

## Where the call is made from

The `request` operation runs inside the Directus process. In Docker, `localhost` in the URL is the Directus container, not your machine and not your dev server. Point it at a name that container can reach (another service on the same Compose network, or a public URL). A frontend dev server on the host is reachable only if the container has a route to the host, for example `host.docker.internal` with `extra_hosts: ["host.docker.internal:host-gateway"]` on Linux. This part was not tested here.

## Failure handling

A failed call does not undo the content change (the trigger is `action`). Attach a `log` operation to the `request` operation's reject path (`{{ $last }}` holds the error) so a wrong secret or an unreachable app shows up in the Directus logs instead of silently leaving the site stale. Add a time-based safety net on the frontend side as well, so a missed webhook heals itself.
