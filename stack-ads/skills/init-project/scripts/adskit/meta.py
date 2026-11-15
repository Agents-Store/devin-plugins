"""Meta Marketing API (Graph API) calls for Facebook and Instagram ads."""
from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path

from . import guards
from .core import AdsError, HttpError, Refused, guess_type, join_url, multipart, read_file, request

GRAPH_ROOT = "https://graph.facebook.com"
VALIDATED_EDGES = ("campaigns", "adsets", "adcreatives", "ads")
DEFAULT_INSIGHT_FIELDS = ("campaign_name,adset_name,ad_name,impressions,reach,clicks,spend,ctr,cpc,cpm,"
                          "actions,cost_per_action_type")
AD_LIBRARY_FIELDS = ("id,page_id,page_name,ad_creative_bodies,ad_creative_link_titles,ad_creative_link_descriptions,"
                     "ad_delivery_start_time,ad_delivery_stop_time,ad_snapshot_url,publisher_platforms,languages")
HINTS = {
    190: "the access token is invalid or expired: generate a new system-user token and put it in ads/.env",
    200: "the token lacks a permission or the system user is not assigned to this asset",
    294: "the app needs the ads_management permission (Marketing API product) for this ad account",
    100: "a parameter is wrong: read error_user_msg and the subcode",
    17: "rate limit of the ad account reached: wait and retry later",
    4: "app-level rate limit reached: wait and retry later",
    613: "rate limit reached: wait and retry later",
    368: "Meta blocked the action as abusive or policy-violating: review the account quality page",
}


def account(ctx):
    value = ctx.key("META_AD_ACCOUNT_ID").strip()
    return value if value.startswith("act_") else "act_" + value


def expand(ctx, text):
    """Replace {account}, {page}, {pixel} and {instagram} with the ids from ads/.env."""
    if not isinstance(text, str) or "{" not in text:
        return text
    names = {"{account}": lambda: account(ctx), "{page}": lambda: ctx.key("META_PAGE_ID"),
             "{pixel}": lambda: ctx.key("META_PIXEL_ID"), "{instagram}": lambda: ctx.key("META_INSTAGRAM_USER_ID")}
    for marker, value in names.items():
        if marker in text:
            text = text.replace(marker, value())
    return text


def expand_all(ctx, value):
    if isinstance(value, dict):
        return {k: expand_all(ctx, v) for k, v in value.items()}
    if isinstance(value, list):
        return [expand_all(ctx, v) for v in value]
    return expand(ctx, value)


def url(ctx, path):
    return join_url(GRAPH_ROOT, ctx.api("meta_graph"), expand(ctx, path))


def own_account(ctx, path):
    """A literal act_ id in a write must be the account of ads/.env: that is the one the dry run looked at."""
    first = str(path).strip("/").split("/")[0]
    if first.startswith("act_") and first != account(ctx):
        raise Refused("the path names ad account %s, but ads/.env holds another one" % first,
                      "write {account} in the path; to work on another account, change META_AD_ACCOUNT_ID")


def headers(ctx):
    return {"Authorization": "Bearer " + ctx.key("META_ACCESS_TOKEN")}


def encode(ctx, params):
    """Graph API takes nested values as JSON text and booleans as true/false."""
    out = {}
    for key, value in expand_all(ctx, params or {}).items():
        if isinstance(value, bool):
            out[key] = "true" if value else "false"
        elif isinstance(value, (dict, list)):
            out[key] = json.dumps(value, ensure_ascii=False)
        elif value is not None:
            out[key] = str(value)
    secret = ctx.key("META_APP_SECRET", required=False)
    if secret:
        out["appsecret_proof"] = hmac.new(secret.encode(), ctx.key("META_ACCESS_TOKEN").encode(), hashlib.sha256).hexdigest()
    return out


def _call(ctx, method, target, params=None, data=None, extra_headers=None, timeout=120):
    sent = headers(ctx)
    sent.update(extra_headers or {})
    try:
        return request(method, target, headers=sent, params=params, data=data, timeout=timeout).json()
    except HttpError as exc:
        error = (exc.json() or {}).get("error", {})
        if not error:
            raise
        code = error.get("code")
        message = "Meta error %s" % code
        if error.get("error_subcode"):
            message += "/%s" % error["error_subcode"]
        message += ": %s" % (error.get("error_user_msg") or error.get("message") or "")
        if error.get("fbtrace_id"):
            message += " (fbtrace_id %s)" % error["fbtrace_id"]
        failure = AdsError(message, HINTS.get(code, ""))
        failure.platform_code, failure.platform_subcode = code, error.get("error_subcode")
        raise failure


def get(ctx, path, params=None):
    guards.meta_read(path, params)
    return _call(ctx, "GET", url(ctx, path), params=encode(ctx, params))


def get_all(ctx, path, params=None, limit=None):
    """Follow paging cursors and return every row."""
    guards.meta_read(path, params)
    rows, target, query = [], url(ctx, path), encode(ctx, params)
    while target:
        page = _call(ctx, "GET", target, params=query)
        rows.extend(page.get("data", []))
        if limit and len(rows) >= limit:
            return rows[:limit]
        target, query = page.get("paging", {}).get("next"), None
    return rows


def post(ctx, path, params=None, yes=False, activate=False, preview=False, plan=False):
    """A write. Without yes: campaigns, ad sets, creatives and ads are validated by Meta, the rest is only shown.

    preview: a single command shown without --yes may describe a call that switches delivery on;
    sending it still needs activate. A launch plan never gets this leniency, and plan=True
    holds a step to creating new objects under the ad account.
    """
    params = dict(params or {})
    summary = guards.meta_request("POST", path, params, ctx.config, activate=activate or (preview and not yes), plan=plan)
    own_account(ctx, path)
    note = guards.activation_note(summary, activate)
    edge = path.strip("/").split("/")[-1]
    if not yes and edge not in VALIDATED_EDGES:
        out = {"dry_run": True, "summary": summary, "would_send": {"path": expand(ctx, path), "params": expand_all(ctx, params)}}
    else:
        if not yes:
            params["execution_options"] = ["validate_only"]
        out = {"validated_only": not yes, "summary": summary,
               "response": _call(ctx, "POST", url(ctx, path), data=encode(ctx, params))}
    if note:
        out["note"] = note
    return out


def delete(ctx, path, yes=False):
    guards.meta_path(path)
    own_account(ctx, path)
    if not yes:
        return {"dry_run": True, "would_delete": expand(ctx, path)}
    return _call(ctx, "DELETE", url(ctx, path), params=encode(ctx, {}))


def upload_image(ctx, file, yes=False):
    path = Path(file)
    content = read_file(path)
    if not yes:
        return {"dry_run": True, "would_upload": str(path), "bytes": len(content), "to": account(ctx) + " image library"}
    ctype, body = multipart(encode(ctx, {}), [("filename", path.name, content, guess_type(path))])
    data = _call(ctx, "POST", url(ctx, "{account}/adimages"), data=body, extra_headers={"Content-Type": ctype}, timeout=300)
    images = data.get("images", {})
    if not images:
        raise AdsError("Meta returned no image: %s" % json.dumps(data)[:300])
    name, info = next(iter(images.items()))
    return {"hash": info.get("hash"), "url": info.get("url"), "name": name, "width": info.get("width"), "height": info.get("height")}


def upload_video(ctx, file, name=None, yes=False):
    path = Path(file)
    content = read_file(path)
    if not yes:
        return {"dry_run": True, "would_upload": str(path), "bytes": len(content), "to": account(ctx) + " video library"}
    fields = encode(ctx, {"name": name or path.stem})
    ctype, body = multipart(fields, [("source", path.name, content, guess_type(path))])
    data = _call(ctx, "POST", url(ctx, "{account}/advideos"), data=body, extra_headers={"Content-Type": ctype}, timeout=900)
    if not data.get("id"):
        raise AdsError("Meta returned no video id: %s" % json.dumps(data)[:300])
    return {"id": data["id"]}


def insights(ctx, obj=None, level="campaign", preset=None, since=None, until=None, fields=None, breakdowns=None, extra=None):
    params = {"level": level, "fields": fields or DEFAULT_INSIGHT_FIELDS, "limit": 500}
    if since or until:
        if not (since and until):
            raise Refused("give both --since and --until, or use --preset")
        params["time_range"] = {"since": since, "until": until}
    else:
        params["date_preset"] = preset or "last_7d"
    if breakdowns:
        params["breakdowns"] = breakdowns
    params.update(extra or {})
    return get_all(ctx, "%s/insights" % (obj or "{account}"), params)


def search(ctx, kind, q=None, extra=None):
    params = {"type": kind, "limit": 50}
    if q:
        params["q"] = q
    params.update(extra or {})
    return get(ctx, "search", params).get("data", [])


def ad_library(ctx, terms, countries, limit=50):
    codes = [c.strip().upper() for c in countries.split(",") if c.strip()]
    if not codes:
        raise Refused("--countries is required, for example DE,FR")
    params = {"search_terms": terms, "ad_type": "ALL", "ad_active_status": "ALL", "ad_reached_countries": codes,
              "fields": AD_LIBRARY_FIELDS, "limit": min(int(limit), 100)}
    return get_all(ctx, "ads_archive", params, limit=int(limit))


def set_status(ctx, object_id, status, yes=False):
    return post(ctx, str(object_id), {"status": status}, yes=yes, activate=status == "ACTIVE")


def account_info(ctx):
    """One read-only look at the account: a line for people and the currency the account is billed in."""
    me = get(ctx, "me", {"fields": "id,name"})
    info = get(ctx, "{account}", {"fields": "name,account_status,currency,amount_spent"})
    states = {1: "active", 2: "disabled", 3: "unsettled", 7: "pending review", 9: "in grace period", 101: "closed"}
    status = states.get(info.get("account_status"), info.get("account_status"))
    note = "token of %s; ad account %s, currency %s, status %s" % (me.get("name", "?"), info.get("name", "?"),
                                                                 info.get("currency"), status)
    return {"note": note, "currency": info.get("currency")}


def check(ctx):
    return account_info(ctx)["note"]
