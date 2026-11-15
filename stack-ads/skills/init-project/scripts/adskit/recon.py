"""Research calls: Firecrawl (pages and brand kit), Apify (ad libraries, social, reviews), DataForSEO (keywords, SERP)."""
from __future__ import annotations

import base64
import json

from .core import AdsError, HttpError, Refused, join_url, request

FIRECRAWL_ROOT = "https://api.firecrawl.dev/v2"
APIFY_ROOT = "https://api.apify.com/v2"
DATAFORSEO_ROOT = "https://api.dataforseo.com/v3"
DATAFORSEO_SANDBOX = "https://sandbox.dataforseo.com/v3"
APIFY_DONE = ("SUCCEEDED", "FAILED", "TIMED-OUT", "ABORTED")


# ── Firecrawl ────────────────────────────────────────────────────────────

def _firecrawl(ctx, method, path, body=None, timeout=180):
    try:
        data = request(method, join_url(FIRECRAWL_ROOT, path), headers={"Authorization": "Bearer " + ctx.key("FIRECRAWL_API_KEY")},
                       json_body=body, timeout=timeout).json()
    except HttpError as exc:
        hint = {401: "the key is wrong or revoked", 402: "the account is out of credits",
                429: "rate limit of the plan reached: wait and retry"}.get(exc.status, "")
        raise AdsError("Firecrawl error %s: %s" % (exc.status, (exc.json() or {}).get("error", exc.body[:300])), hint)
    if isinstance(data, dict) and data.get("success") is False:
        raise AdsError("Firecrawl reported a failure: %s" % data.get("error", "no detail"))
    return data


def firecrawl_scrape(ctx, target, formats="markdown", schema=None, prompt=None):
    wanted = [f.strip() for f in formats.split(",") if f.strip()]
    if schema is not None or prompt:
        extract = {"type": "json"}
        if schema is not None:
            extract["schema"] = schema
        if prompt:
            extract["prompt"] = prompt
        wanted.append(extract)
    return _firecrawl(ctx, "POST", "scrape", {"url": target, "formats": wanted})


def firecrawl_search(ctx, query, limit=10):
    return _firecrawl(ctx, "POST", "search", {"query": query, "limit": int(limit)})


def firecrawl_map(ctx, target, limit=200, search=None):
    body = {"url": target, "limit": int(limit)}
    if search:
        body["search"] = search
    return _firecrawl(ctx, "POST", "map", body)


def check_firecrawl(ctx):
    data = _firecrawl(ctx, "GET", "team/credit-usage").get("data", {})
    return "%s credits left" % data.get("remainingCredits", "?")


# ── Apify ────────────────────────────────────────────────────────────────

def actor_id(actor):
    """Accept username/actor-name and the API form username~actor-name."""
    return actor.strip().replace("/", "~")


def _apify(ctx, method, path, params=None, body=None, timeout=120):
    try:
        return request(method, join_url(APIFY_ROOT, path), headers={"Authorization": "Bearer " + ctx.key("APIFY_TOKEN")},
                       params=params, json_body=body, timeout=timeout).json()
    except HttpError as exc:
        error = (exc.json() or {}).get("error", {})
        hint = {401: "the token is wrong or revoked: create a new personal API token in the Apify console",
                402: "the monthly usage limit or the run's spend cap is reached",
                404: "no such Actor or run: check the id (username/actor-name)",
                429: "too many requests: wait and retry"}.get(exc.status, "")
        raise AdsError("Apify error %s: %s" % (error.get("type", exc.status), error.get("message", exc.body[:300])), hint)


def apify_actor(ctx, actor):
    info = _apify(ctx, "GET", join_url("acts", actor_id(actor))).get("data", {})
    out = {"id": "%s/%s" % (info.get("username"), info.get("name")), "title": info.get("title"),
           "description": (info.get("description") or "")[:300], "modified_at": info.get("modifiedAt"),
           "users_30_days": (info.get("stats") or {}).get("totalUsers30Days"), "pricing": info.get("pricingInfos") or []}
    try:
        build = _apify(ctx, "GET", join_url("acts", actor_id(actor), "builds", "default")).get("data", {})
        schema = build.get("inputSchema") or (build.get("actorDefinition") or {}).get("input")
        if isinstance(schema, str):
            schema = json.loads(schema)
        fields = []
        for name, spec in ((schema or {}).get("properties") or {}).items():
            fields.append({"name": name, "type": spec.get("type"), "required": name in (schema.get("required") or []),
                           "description": (spec.get("description") or spec.get("title") or "")[:140]})
        out["input"] = fields
    except (AdsError, ValueError):
        out["input"] = "not available: read the Actor's page"
    return out


def apify_run(ctx, actor, payload, max_usd=None, max_items=None, timeout=900):
    """Start an Actor with a spend cap, wait for it and return the dataset items."""
    if max_usd is None:
        max_usd = ctx.config.get("guardrails", {}).get("max_research_usd_per_call", 1.0)
    params = {"maxTotalChargeUsd": max_usd, "timeout": int(timeout)}
    if max_items:
        params["maxItems"] = int(max_items)
    run = _apify(ctx, "POST", join_url("acts", actor_id(actor), "runs"), params=params, body=payload or {}).get("data", {})
    waited = 0
    while run.get("status") not in APIFY_DONE:
        if waited > timeout + 120:
            raise AdsError("Apify run %s is still %s" % (run.get("id"), run.get("status")),
                           "it keeps running on Apify: abort it in the console if it is no longer needed")
        run = _apify(ctx, "GET", join_url("actor-runs", run["id"]), params={"waitForFinish": 60}, timeout=90).get("data", {})
        waited += 60
    if run.get("status") != "SUCCEEDED":
        raise AdsError("Apify run %s ended as %s" % (run.get("id"), run.get("status")),
                       "open the run log in the Apify console; an input field is the usual cause")
    params = {"clean": "true", "format": "json"}
    if max_items:
        params["limit"] = int(max_items)
    resp = request("GET", join_url(APIFY_ROOT, "datasets", run["defaultDatasetId"], "items"),
                   headers={"Authorization": "Bearer " + ctx.key("APIFY_TOKEN")}, params=params, timeout=300)
    items = resp.json()
    return {"run_id": run.get("id"), "usage_usd": run.get("usageTotalUsd"), "items": items}


def check_apify(ctx):
    data = _apify(ctx, "GET", join_url("users", "me")).get("data", {})
    plan = (data.get("plan") or {}).get("id", "?")
    return "account on plan %s" % plan


# ── DataForSEO ───────────────────────────────────────────────────────────

def dataforseo(ctx, method, path, body=None, sandbox=False):
    login, password = ctx.key("DATAFORSEO_USERNAME"), ctx.key("DATAFORSEO_PASSWORD")
    token = base64.b64encode(("%s:%s" % (login, password)).encode("utf-8")).decode("ascii")
    route = path.strip("/")
    if route.startswith("v3/"):
        route = route[3:]
    if method == "POST" and isinstance(body, dict):
        body = [body]
    try:
        data = request(method, join_url(DATAFORSEO_SANDBOX if sandbox else DATAFORSEO_ROOT, route),
                       headers={"Authorization": "Basic " + token}, json_body=body if method == "POST" else None,
                       timeout=180).json()
    except HttpError as exc:
        payload = exc.json() or {}
        hint = "the API login or API password is wrong: copy both from the API Access page" if exc.status == 401 else ""
        raise AdsError("DataForSEO error %s: %s" % (payload.get("status_code", exc.status),
                                                    payload.get("status_message", exc.body[:300])), hint)
    if data.get("status_code") != 20000:
        raise AdsError("DataForSEO error %s: %s" % (data.get("status_code"), data.get("status_message")))
    failed = [t for t in data.get("tasks") or [] if t.get("status_code", 20000) >= 40000]
    if failed:
        first = failed[0]
        hint = "top up the balance" if first.get("status_code") == 40200 else "compare the body with the endpoint's field table"
        raise AdsError("DataForSEO task error %s: %s" % (first.get("status_code"), first.get("status_message")), hint)
    return data


def check_dataforseo(ctx):
    data = dataforseo(ctx, "GET", "appendix/user_data")
    result = ((data.get("tasks") or [{}])[0].get("result") or [{}])[0]
    balance = (result.get("money") or {}).get("balance")
    return "balance %s USD" % balance if balance is not None else "credentials accepted"


def require_payload(payload, what):
    if payload is None:
        raise Refused("%s needs --data @FILE or --input @FILE with a JSON body" % what)
    return payload
