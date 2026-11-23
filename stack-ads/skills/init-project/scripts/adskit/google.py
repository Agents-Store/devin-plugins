"""Google Ads API and Search Console API over REST, with one OAuth client for both."""
from __future__ import annotations

import json
import urllib.parse
from pathlib import Path

from . import guards
from .core import AdsError, HttpError, Refused, join_url, request, set_env_value

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
ADS_ROOT = "https://googleads.googleapis.com"
GSC_ROOT = "https://www.googleapis.com/webmasters/v3"
SCOPES = {
    "ads": "https://www.googleapis.com/auth/adwords",
    "gsc": "https://www.googleapis.com/auth/webmasters.readonly",
}
_TOKENS = {}


# ── OAuth ────────────────────────────────────────────────────────────────

def redirect_uri(port):
    return "http://localhost:%d" % int(port)


def login_url(ctx, port=8080, scopes="ads,gsc"):
    names = [s.strip() for s in scopes.split(",") if s.strip()]
    unknown = [s for s in names if s not in SCOPES]
    if unknown:
        raise Refused("unknown scope %s; use ads, gsc or both" % ", ".join(unknown))
    query = {
        "client_id": ctx.key("GOOGLE_ADS_CLIENT_ID"),
        "redirect_uri": redirect_uri(port),
        "response_type": "code",
        "scope": " ".join(SCOPES[s] for s in names),
        "access_type": "offline",
        # select_account: the login that owns the ad account is often not the one the browser is signed in with
        "prompt": "select_account consent",
    }
    return AUTH_URL + "?" + urllib.parse.urlencode(query)


def login_exchange(ctx, redirect_url, port=8080):
    """Trade the code in the pasted redirect URL for a refresh token and store it."""
    parsed = urllib.parse.urlsplit(redirect_url.strip())
    query = urllib.parse.parse_qs(parsed.query)
    if "error" in query:
        raise AdsError("Google returned %s" % query["error"][0], "open the consent URL again and allow access")
    code = query.get("code", [redirect_url.strip() if "=" not in redirect_url else ""])[0]
    if not code:
        raise Refused("no code found in the pasted URL", "paste the whole address the browser ended on")
    try:
        resp = request("POST", TOKEN_URL, data={
            "grant_type": "authorization_code", "code": code,
            "client_id": ctx.key("GOOGLE_ADS_CLIENT_ID"), "client_secret": ctx.key("GOOGLE_ADS_CLIENT_SECRET"),
            "redirect_uri": redirect_uri(port)}).json()
    except HttpError as exc:
        raise AdsError("the code was not accepted: %s" % exc.message,
                       "a code works once and for a few minutes: run google login again and use a fresh URL")
    token = resp.get("refresh_token")
    if not token:
        raise AdsError("Google returned no refresh token",
                       "remove the app under myaccount.google.com permissions, then run google login again")
    set_env_value(ctx.ws, "GOOGLE_ADS_REFRESH_TOKEN", token)
    ctx.env["GOOGLE_ADS_REFRESH_TOKEN"] = token
    return {"stored": "GOOGLE_ADS_REFRESH_TOKEN", "scope": resp.get("scope", "")}


def import_adc(ctx, file=None):
    path = Path(file).expanduser() if file else Path.home() / ".config" / "gcloud" / "application_default_credentials.json"
    if not path.is_file():
        raise Refused("no credentials file at %s" % path, "run gcloud auth application-default login first")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("type") != "authorized_user":
        raise Refused("that file holds %r credentials, not a user refresh token" % data.get("type"))
    for name, field in (("GOOGLE_ADS_CLIENT_ID", "client_id"), ("GOOGLE_ADS_CLIENT_SECRET", "client_secret"),
                        ("GOOGLE_ADS_REFRESH_TOKEN", "refresh_token")):
        set_env_value(ctx.ws, name, data[field])
        ctx.env[name] = data[field]
    return {"stored": ["GOOGLE_ADS_CLIENT_ID", "GOOGLE_ADS_CLIENT_SECRET", "GOOGLE_ADS_REFRESH_TOKEN"]}


def export_adc(ctx, file=None):
    """Write the stored OAuth credentials in the application-default format the google-ads MCP server reads."""
    target = Path(file).expanduser() if file else ctx.ws / ".google-adc.json"
    data = {"type": "authorized_user", "client_id": ctx.key("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": ctx.key("GOOGLE_ADS_CLIENT_SECRET"), "refresh_token": ctx.key("GOOGLE_ADS_REFRESH_TOKEN")}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    try:
        target.chmod(0o600)
    except OSError:
        pass
    absolute = str(target.resolve())
    set_env_value(ctx.ws, "GOOGLE_APPLICATION_CREDENTIALS", absolute)
    return {"written": str(target), "stored": "GOOGLE_APPLICATION_CREDENTIALS",
            "next": "set GOOGLE_CLOUD_PROJECT in ads/.env, run env sync-claude, restart the session"}


def access_token(ctx):
    ready = ctx.key("GOOGLE_ACCESS_TOKEN", required=False)
    if ready:
        return ready
    refresh = ctx.key("GOOGLE_ADS_REFRESH_TOKEN")
    if refresh in _TOKENS:
        return _TOKENS[refresh]
    try:
        resp = request("POST", TOKEN_URL, data={
            "grant_type": "refresh_token", "refresh_token": refresh,
            "client_id": ctx.key("GOOGLE_ADS_CLIENT_ID"), "client_secret": ctx.key("GOOGLE_ADS_CLIENT_SECRET")}).json()
    except HttpError as exc:
        detail = (exc.json() or {}).get("error", "")
        hint = "run google login again"
        if detail == "invalid_grant":
            hint += "; a refresh token dies after 7 days while the OAuth consent screen is in Testing: publish it first"
        failure = AdsError("Google refused the refresh token (%s)" % (detail or exc.status), hint)
        failure.before_send = True          # no request reached the Ads API, so nothing can have been created
        raise failure
    except AdsError as exc:
        exc.before_send = True
        raise
    _TOKENS[refresh] = resp["access_token"]
    return _TOKENS[refresh]


# ── Google Ads ───────────────────────────────────────────────────────────

def customer_id(ctx, override=None):
    value = (override or ctx.key("GOOGLE_ADS_CUSTOMER_ID")).replace("-", "").strip()
    if not value.isdigit():
        raise Refused("a Google Ads customer id is 10 digits, got %r" % value)
    return value


def ads_headers(ctx):
    headers = {"Authorization": "Bearer " + access_token(ctx)}
    login = ctx.key("GOOGLE_ADS_LOGIN_CUSTOMER_ID", required=False).replace("-", "")
    if login:
        headers["login-customer-id"] = login
    return headers


def ads_url(ctx, *parts):
    return join_url(ADS_ROOT, ctx.api("google_ads"), *parts)


def explain_failure(exc):
    """Turn a GoogleAdsFailure into one line per error: operation, field path, code, message."""
    payload = exc.json() or {}
    error = payload[0].get("error", {}) if isinstance(payload, list) and payload else payload.get("error", {})
    lines = []
    for detail in error.get("details", []):
        for item in detail.get("errors", []):
            path = ".".join(
                "%s[%s]" % (e.get("fieldName"), e["index"]) if "index" in e else str(e.get("fieldName"))
                for e in item.get("location", {}).get("fieldPathElements", []))
            code = ", ".join("%s=%s" % kv for kv in item.get("errorCode", {}).items())
            lines.append("%s: %s (%s)" % (path or "request", item.get("message", ""), code))
    if not lines and error.get("message"):
        lines.append("%s (%s)" % (error["message"], error.get("status", exc.status)))
    return lines


def _ads_call(ctx, method, url, body=None):
    try:
        return request(method, url, headers=ads_headers(ctx), json_body=body, timeout=120).json()
    except HttpError as exc:
        lines = explain_failure(exc)
        if not lines:
            raise
        hint = ""
        text = " ".join(lines)
        if "CLOUD_PROJECT_NOT_APPROVED_FOR_PRODUCTION" in text:
            hint = "the Cloud project has Test access only: apply for Explorer on the Google Ads API overview page"
        elif "USER_PERMISSION_DENIED" in text:
            hint = "set GOOGLE_ADS_LOGIN_CUSTOMER_ID to the manager account, or grant this user access to the account"
        elif "NOT_ADS_USER" in text:
            hint = ("this Google login has no Google Ads account: run google login again and pick the login that opens "
                    "the account at ads.google.com (it need not be the login that owns the Cloud project)")
        elif "explorer access" in text.lower():
            hint = "this method needs Basic access: apply for it on the Google Ads API overview page (keys guide, step 2)"
        raise AdsError("Google Ads refused the request:\n  " + "\n  ".join(lines), hint)


def customers(ctx):
    return _ads_call(ctx, "GET", ads_url(ctx, "customers:listAccessibleCustomers")).get("resourceNames", [])


def search(ctx, query, customer=None):
    url = ads_url(ctx, "customers", customer_id(ctx, customer), "googleAds:search")
    rows, token = [], None
    while True:
        body = {"query": query}
        if token:
            body["pageToken"] = token
        page = _ads_call(ctx, "POST", url, body)
        rows.extend(page.get("results", []))
        token = page.get("nextPageToken")
        if not token:
            return rows


def mutate(ctx, body, customer=None, yes=False, activate=False, partial_failure=False, preview=False, plan=None):
    """googleAds:mutate. Validation only unless yes is set. {customer} in the body becomes the account id.

    The body is rewritten to camelCase field names first, so the rules judge exactly what is sent.
    preview: a single command shown without --yes may describe a call that switches delivery on;
    sending it still needs activate. A launch plan never gets this leniency; plan is the set of
    resource names its earlier steps created, and holds a step to creating new objects.
    """
    account = customer_id(ctx, customer)
    body = guards.google_canonical(json.loads(json.dumps(body).replace("{customer}", account)))
    summary = guards.google_mutate(body, guards.for_platform(ctx.config, "google"), activate=activate or (preview and not yes), plan=plan)
    payload = {key: value for key, value in body.items() if key != "partialFailure"}
    payload["validateOnly"] = not yes
    if partial_failure:
        payload["partialFailure"] = True
    url = ads_url(ctx, "customers", account, "googleAds:mutate")
    response = _ads_call(ctx, "POST", url, payload)
    out = {"validated_only": not yes, "summary": summary, "results": result_names(response), "response": response}
    note = guards.activation_note(summary, activate)
    if note:
        out["note"] = note
    failure = response.get("partialFailureError")
    if failure:
        # Google applied the operations that passed and skipped the rest: the caller must not read this as done.
        out["partial_failure"] = failure.get("message") or json.dumps(failure)[:300]
    return out


def result_names(response):
    names = []
    for item in response.get("mutateOperationResponses", []):
        value = next(iter(item.values()), {}) if item else {}
        names.append(value.get("resourceName") if isinstance(value, dict) else None)
    return names


def keyword_ideas(ctx, keywords=None, url=None, geo="", language="", limit=100, customer=None):
    words = [k.strip() for k in (keywords or "").split(",") if k.strip()]
    if not words and not url:
        raise Refused("give --keywords, --url or both")
    body = {"keywordPlanNetwork": "GOOGLE_SEARCH", "includeAdultKeywords": False, "pageSize": int(limit)}
    if words and url:
        body["keywordAndUrlSeed"] = {"keywords": words[:20], "url": url}
    elif words:
        body["keywordSeed"] = {"keywords": words[:20]}
    else:
        body["urlSeed"] = {"url": url}
    ids = [g.strip() for g in str(geo).split(",") if g.strip()]
    if ids:
        body["geoTargetConstants"] = ["geoTargetConstants/%s" % g.split("/")[-1] for g in ids]
    if language:
        body["language"] = "languageConstants/%s" % str(language).split("/")[-1]
    target = ads_url(ctx, "customers", customer_id(ctx, customer) + ":generateKeywordIdeas")
    rows = []
    for item in _ads_call(ctx, "POST", target, body).get("results", []):
        metrics = item.get("keywordIdeaMetrics", {})
        rows.append({
            "keyword": item.get("text"),
            "avg_monthly_searches": int(metrics.get("avgMonthlySearches", 0) or 0),
            "competition": metrics.get("competition"),
            "competition_index": metrics.get("competitionIndex"),
            "bid_low": _micros(metrics.get("lowTopOfPageBidMicros")),
            "bid_high": _micros(metrics.get("highTopOfPageBidMicros")),
        })
    return rows


def _micros(value):
    return round(int(value) / 1_000_000, 2) if value not in (None, "") else None


def geo(ctx, names, country=None, locale="en"):
    body = {"locale": locale, "locationNames": {"names": [n.strip() for n in names.split(",") if n.strip()][:25]}}
    if country:
        body["countryCode"] = country.upper()
    data = _ads_call(ctx, "POST", ads_url(ctx, "geoTargetConstants:suggest"), body)
    rows = []
    for item in data.get("geoTargetConstantSuggestions", []):
        target = item.get("geoTargetConstant", {})
        rows.append({"id": target.get("id") or str(target.get("resourceName", "")).split("/")[-1],
                     "resource_name": target.get("resourceName"), "name": target.get("canonicalName") or target.get("name"),
                     "country": target.get("countryCode"), "type": target.get("targetType"), "reach": item.get("reach")})
    return rows


def call(ctx, method, path, body=None, yes=False):
    """A read, or a conversion upload, by its REST path. {customer} becomes the account id from ads/.env.

    Nothing that shapes a campaign is sent from here: guards.google_call refuses every ...:mutate
    method and its relatives, so the paused rule and the budget ceilings cannot be walked around.
    """
    method = method.upper()
    path = path.strip("/")
    kind = guards.google_call(method, path.replace("{customer}", "0"))     # refused before any key is read
    if "{customer}" in path or (body is not None and "{customer}" in json.dumps(body)):
        account = customer_id(ctx)
        path = path.replace("{customer}", account)
        if body is not None:
            body = json.loads(json.dumps(body).replace("{customer}", account))
    if kind == "write" and not yes:
        return {"dry_run": True, "would_send": {"method": method, "path": path, "body": body}}
    return _ads_call(ctx, method, ads_url(ctx, path), body)


def enable_campaigns(ctx, resource_names, customer=None, yes=False):
    body = {"mutateOperations": [
        {"campaignOperation": {"update": {"resourceName": name, "status": "ENABLED"}, "updateMask": "status"}}
        for name in resource_names]}
    return mutate(ctx, body, customer=customer, yes=yes, activate=True)


def set_status(ctx, resource_names, status, customer=None, yes=False):
    operations = []
    for name in resource_names:
        kind = name.split("/")[2] if name.count("/") >= 3 else ""
        key = {"campaigns": "campaignOperation", "adGroups": "adGroupOperation", "adGroupAds": "adGroupAdOperation",
               "assetGroups": "assetGroupOperation"}.get(kind)
        if not key:
            continue
        if status == "REMOVED":
            operations.append({key: {"remove": name}})
        else:
            operations.append({key: {"update": {"resourceName": name, "status": status}, "updateMask": "status"}})
    if not operations:
        return {"skipped": "nothing to change"}
    return mutate(ctx, {"mutateOperations": operations}, customer=customer, yes=yes, activate=status == "ENABLED")


def account_info(ctx):
    """One read-only look at the account: a line for people and the currency the account is billed in."""
    accounts = customers(ctx)
    note, currency = "%d reachable account(s)" % len(accounts), None
    if ctx.key("GOOGLE_ADS_CUSTOMER_ID", required=False):
        rows = search(ctx, "SELECT customer.id, customer.descriptive_name, customer.currency_code, customer.status FROM customer LIMIT 1")
        info = rows[0].get("customer", {}) if rows else {}
        currency = info.get("currencyCode")
        note += "; account %s, currency %s, status %s" % (info.get("id"), currency, info.get("status"))
    return {"note": note, "currency": currency}


def check(ctx):
    return account_info(ctx)["note"]


# ── Search Console ───────────────────────────────────────────────────────

def _gsc(ctx, method, url, body=None):
    try:
        return request(method, url, headers={"Authorization": "Bearer " + access_token(ctx)}, json_body=body, timeout=120).json()
    except HttpError as exc:
        hint = ""
        if exc.status == 403:
            hint = ("the refresh token lacks the Search Console scope or the user has no access to the property: "
                    "run google login --scopes ads,gsc, and check Settings > Users and permissions in Search Console")
        raise AdsError("Search Console refused the request: %s" % exc.message, hint)


def gsc_sites(ctx):
    return _gsc(ctx, "GET", join_url(GSC_ROOT, "sites")).get("siteEntry", [])


def gsc_query(ctx, site, start, end, dimensions="query", row_limit=1000, search_type="web", filters=None, data_state="final"):
    site = site or ctx.key("GSC_SITE_URL")
    dims = [d.strip() for d in dimensions.split(",") if d.strip()]
    body = {"startDate": start, "endDate": end, "dimensions": dims, "type": search_type, "dataState": data_state}
    parsed = []
    for item in filters or []:
        parts = item.split(":", 2)
        if len(parts) != 3:
            raise Refused("a filter looks like DIMENSION:OPERATOR:VALUE, got %r" % item)
        parsed.append({"dimension": parts[0], "operator": parts[1], "expression": parts[2]})
    if parsed:
        body["dimensionFilterGroups"] = [{"groupType": "and", "filters": parsed}]
    url = join_url(GSC_ROOT, "sites", urllib.parse.quote(site, safe=""), "searchAnalytics", "query")
    rows, offset, wanted = [], 0, int(row_limit)
    while len(rows) < wanted:
        body["rowLimit"] = min(25000, wanted - len(rows))
        body["startRow"] = offset
        page = _gsc(ctx, "POST", url, body).get("rows", [])
        for row in page:
            flat = dict(zip(dims, row.get("keys", [])))
            flat.update({"clicks": row.get("clicks"), "impressions": row.get("impressions"),
                         "ctr": round(row.get("ctr", 0), 4), "position": round(row.get("position", 0), 1)})
            rows.append(flat)
        if len(page) < body["rowLimit"]:
            break
        offset += len(page)
    return rows


def check_gsc(ctx):
    sites = [s.get("siteUrl") for s in gsc_sites(ctx)]
    wanted = ctx.key("GSC_SITE_URL", required=False)
    if wanted and wanted not in sites:
        raise AdsError("GSC_SITE_URL %s is not among the %d properties this user can read" % (wanted, len(sites)),
                       "run gsc sites and copy the property exactly, for example sc-domain:example.com")
    return "%d readable propert%s" % (len(sites), "y" if len(sites) == 1 else "ies")
