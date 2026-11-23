"""TikTok API for Business (Marketing API) calls."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from . import guards
from .core import AdsError, Refused, guess_type, join_url, multipart, read_file, request, set_env_value

API_ROOT = "https://business-api.tiktok.com/open_api"
READ_TAILS = guards.TIKTOK_READ_TAILS
DEFAULT_METRICS = "spend,impressions,clicks,ctr,cpc,cpm,conversion,cost_per_conversion,conversion_rate"
LEVEL_DIMENSION = {"AUCTION_ADVERTISER": "advertiser_id", "AUCTION_CAMPAIGN": "campaign_id",
                   "AUCTION_ADGROUP": "adgroup_id", "AUCTION_AD": "ad_id"}
STATUS_FIELDS = {"campaign": "campaign_ids", "adgroup": "adgroup_ids", "ad": "ad_ids"}
STATUS_BATCH = 20
HINTS = {
    40001: "the access token or advertiser id is wrong, or the app lacks the permission scope for this endpoint",
    40002: "a parameter is missing or malformed: compare the body with the endpoint's field table",
    40100: "too many requests for this app: slow down and retry",
    40105: "the access token is invalid or was revoked: authorize the app again and run tiktok oauth-exchange",
    40133: "too many requests for this advertiser: slow down and retry",
    40118: "the account is not allowlisted for this feature",
}


def url(ctx, path):
    # The API rejects a path without the trailing slash.
    return join_url(API_ROOT, ctx.api("tiktok"), path) + "/"


def headers(ctx):
    return {"Access-Token": ctx.key("TIKTOK_ACCESS_TOKEN")}


def advertiser(ctx):
    return ctx.key("TIKTOK_ADVERTISER_ID").strip()


def expand_all(ctx, value):
    """Replace {advertiser} and {pixel} with the ids from ads/.env."""
    if isinstance(value, dict):
        return {k: expand_all(ctx, v) for k, v in value.items()}
    if isinstance(value, list):
        return [expand_all(ctx, v) for v in value]
    if isinstance(value, str) and "{" in value:
        if "{advertiser}" in value:
            value = value.replace("{advertiser}", advertiser(ctx))
        if "{pixel}" in value:
            value = value.replace("{pixel}", ctx.key("TIKTOK_PIXEL_ID"))
    return value


def unwrap(payload):
    """TikTok answers HTTP 200 for errors too: the verdict is the code field."""
    code = payload.get("code")
    if code != 0:
        message = "TikTok error %s: %s" % (code, payload.get("message", ""))
        if payload.get("request_id"):
            message += " (request_id %s)" % payload["request_id"]
        error = AdsError(message, HINTS.get(code, ""))
        error.uncertain = isinstance(code, int) and code >= 50000   # TikTok-side failure: the write may have landed
        raise error
    return payload.get("data") or {}


def get(ctx, path, params=None):
    route = guards.tiktok_path(path)
    query = {}
    if route.startswith("oauth2/"):
        query["app_id"] = ctx.key("TIKTOK_APP_ID")
        query["secret"] = ctx.key("TIKTOK_APP_SECRET")
    elif "advertiser_ids" not in (params or {}):
        query["advertiser_id"] = advertiser(ctx)
    for key, value in expand_all(ctx, params or {}).items():
        query[key] = json.dumps(value) if isinstance(value, (dict, list)) else value
    return unwrap(request("GET", url(ctx, route), headers=headers(ctx), params=query, timeout=120).json())


def post(ctx, path, body=None, yes=False, activate=False, preview=False, plan=False):
    """A POST. A read is sent as it is; a write is only shown unless yes is set.

    preview: a single command shown without --yes may describe a call that switches delivery on;
    sending it still needs activate. A launch plan never gets this leniency, and plan=True
    holds a step to creating new objects.
    """
    route = guards.tiktok_path(path)
    body = expand_all(ctx, dict(body or {}))
    reads = route.split("/")[-1] in READ_TAILS
    summary = guards.tiktok_request(route, body, guards.for_platform(ctx.config, "tiktok"), activate=activate or (preview and not yes), plan=plan)
    named = body.get("advertiser_id")
    if not reads and named not in (None, "") and str(named) != advertiser(ctx):
        # The dry run looked at the advertiser of ads/.env; a body that names another would write somewhere else.
        raise Refused("the body names advertiser %s, but ads/.env holds another one" % named,
                      "leave advertiser_id out: the toolkit adds the one from TIKTOK_ADVERTISER_ID")
    if not reads and not yes:
        out = {"dry_run": True, "summary": summary, "would_send": {"path": route + "/", "body": body},
               "note": "TikTok has no validate-only mode: this body is checked by the toolkit only"}
        warning = guards.activation_note(summary, activate)
        if warning:
            out["note"] = "%s. %s" % (warning, out["note"])
        return out
    body.setdefault("advertiser_id", advertiser(ctx))
    data = unwrap(request("POST", url(ctx, route), headers=headers(ctx), json_body=body, timeout=120).json())
    return {"summary": summary, "data": data}


def _upload(ctx, route, kind, file, name, yes):
    path = Path(file)
    content = read_file(path)
    if not yes:
        return {"dry_run": True, "would_upload": str(path), "bytes": len(content), "to": "advertiser " + advertiser(ctx)}
    fields = {"advertiser_id": advertiser(ctx), "upload_type": "UPLOAD_BY_FILE",
              "file_name": name or "%s_%d" % (path.stem, int(time.time())),
              "%s_signature" % kind: hashlib.md5(content).hexdigest()}
    ctype, body = multipart(fields, [("%s_file" % kind, path.name, content, guess_type(path))])
    sent = headers(ctx)
    sent["Content-Type"] = ctype
    return unwrap(request("POST", url(ctx, route), headers=sent, data=body, timeout=900).json())


def upload_video(ctx, file=None, video_url=None, name=None, yes=False):
    if bool(file) == bool(video_url):
        raise Refused("give exactly one of --file and --url")
    if file:
        data = _upload(ctx, "file/video/ad/upload", "video", file, name, yes)
    elif not yes:
        return {"dry_run": True, "would_upload": video_url, "to": "advertiser " + advertiser(ctx)}
    else:
        body = {"advertiser_id": advertiser(ctx), "upload_type": "UPLOAD_BY_URL", "video_url": video_url,
                "file_name": name or "video_%d" % int(time.time())}
        data = unwrap(request("POST", url(ctx, "file/video/ad/upload"), headers=headers(ctx), json_body=body, timeout=300).json())
    if isinstance(data, dict) and data.get("dry_run"):
        return data
    first = data[0] if isinstance(data, list) and data else data
    return {"video_id": first.get("video_id"), "width": first.get("width"), "height": first.get("height"),
            "duration": first.get("duration")}


def upload_image(ctx, file, yes=False):
    data = _upload(ctx, "file/image/ad/upload", "image", file, None, yes)
    if data.get("dry_run"):
        return data
    return {"image_id": data.get("image_id"), "width": data.get("width"), "height": data.get("height")}


def report(ctx, level, start, end, metrics=None, dimensions=None):
    level = level.upper()
    if level not in LEVEL_DIMENSION:
        raise Refused("unknown level %s; use one of %s" % (level, ", ".join(LEVEL_DIMENSION)))
    dims = [d.strip() for d in (dimensions or LEVEL_DIMENSION[level]).split(",") if d.strip()]
    wanted = [m.strip() for m in (metrics or DEFAULT_METRICS).split(",") if m.strip()]
    rows, page = [], 1
    while True:
        data = get(ctx, "report/integrated/get", {
            "report_type": "BASIC", "service_type": "AUCTION", "data_level": level, "dimensions": dims,
            "metrics": wanted, "start_date": start, "end_date": end, "page": page, "page_size": 1000})
        for item in data.get("list", []):
            row = dict(item.get("dimensions", {}))
            row.update(item.get("metrics", {}))
            rows.append(row)
        info = data.get("page_info", {})
        if page >= int(info.get("total_page", 1) or 1):
            return rows
        page += 1


def oauth_exchange(ctx, auth_code, write=False):
    body = {"app_id": ctx.key("TIKTOK_APP_ID"), "secret": ctx.key("TIKTOK_APP_SECRET"), "auth_code": auth_code}
    data = unwrap(request("POST", url(ctx, "oauth2/access_token"), json_body=body, timeout=60).json())
    token = data.get("access_token")
    if not token:
        raise AdsError("TikTok returned no access token")
    ids = data.get("advertiser_ids") or []
    out = {"advertiser_ids": ids, "scope": data.get("scope")}
    if write:
        set_env_value(ctx.ws, "TIKTOK_ACCESS_TOKEN", token)
        ctx.env["TIKTOK_ACCESS_TOKEN"] = token
        out["stored"] = ["TIKTOK_ACCESS_TOKEN"]
        if len(ids) == 1 and not ctx.key("TIKTOK_ADVERTISER_ID", required=False):
            set_env_value(ctx.ws, "TIKTOK_ADVERTISER_ID", str(ids[0]))
            out["stored"].append("TIKTOK_ADVERTISER_ID")
    else:
        out["note"] = "token received but not stored: run again with --write and a fresh code, a code works once"
    return out


def set_status(ctx, level, ids, status, yes=False, smart_plus=False):
    """Enable, pause or delete campaigns, ad groups or ads; TikTok takes at most 20 ids per call."""
    field = "smart_plus_ad_ids" if smart_plus and level == "ad" else STATUS_FIELDS[level]
    route = ("smart_plus/%s/status/update" if smart_plus else "%s/status/update") % level
    ids = [str(i) for i in ids]
    results, refused, reasons = [], [], []
    for start in range(0, len(ids), STATUS_BATCH):
        batch = ids[start:start + STATUS_BATCH]
        try:
            out = post(ctx, route, {field: batch, "operation_status": status}, yes=yes, activate=status == "ENABLE")
        except Refused:
            raise
        except AdsError as exc:
            if status == "ENABLE":
                raise                       # never go on enabling after a failure
            refused.extend(batch)           # pausing and removing go on with the next batch
            reasons.append(exc.message)
            continue
        # A refused object comes back under code 0, named in error_list.
        errors = (out.get("data") or {}).get("error_list") if yes else None
        if errors:
            named = [str(value) for item in errors if isinstance(item, dict)
                     for key, value in item.items() if key.endswith("_id")]
            refused.extend([i for i in batch if i in named] or batch)
            reasons.append(json.dumps(errors, ensure_ascii=False)[:400])
            if status == "ENABLE":
                break                       # never go on enabling after a failure
        results.append(out)
    if refused:
        failure = AdsError("TikTok did not change the status of %d %s object(s): %s"
                           % (len(refused), level, "; ".join(reasons)))
        failure.failed_ids = refused        # the caller keeps what did change
        raise failure
    return results


def account_info(ctx):
    """One read-only look at the account: a line for people and the currency the account is billed in."""
    data = get(ctx, "advertiser/info", {"advertiser_ids": [advertiser(ctx)]})
    info = (data.get("list") or [{}])[0]
    note = "advertiser %s, currency %s, status %s" % (info.get("name", "?"), info.get("currency"), info.get("status"))
    return {"note": note, "currency": info.get("currency")}


def check(ctx):
    return account_info(ctx)["note"]
