"""Guard rails checked before a write reaches an ad platform.

Pure functions: each takes the request about to be sent and either returns a
short summary of what it would do or raises Refused. The rules are the same for
a single command and for a launch plan:

  * what a request does is read from its parameters, so a path carries no
    parameters and a request carries no other requests inside it;
  * everything that can deliver is born paused;
  * a daily budget may not exceed the ceiling in ads/config.json;
  * a lifetime budget is refused until the user sets a ceiling for it;
  * a budget is a plain number that is not negative, and the daily ceiling must be set;
  * switching anything on needs an explicit --activate;
  * a launch plan only creates: it never changes or removes what already exists.

These rules see one request at a time. What a whole launch plan adds up to is
checked in launch.budget_check.
"""
from __future__ import annotations

import math
import re
import urllib.parse

from .core import Refused

# Currencies whose amounts Meta takes without the two implied decimals.
ZERO_DECIMAL = {"CLP", "COP", "CRC", "HUF", "IDR", "ISK", "JPY", "KRW", "PYG", "TWD", "VND"}
META_CREATE_EDGES = ("campaigns", "adsets", "ads")
META_PATH = re.compile(r"[A-Za-z0-9_{}.-]+(/[A-Za-z0-9_{}.-]+)*")
# Parameters that carry further calls or a second object, out of the guard rails' sight.
META_CONTAINERS = ("batch", "adbatch", "asyncbatch", "adset_spec", "campaign_spec")
META_ON = ("ACTIVE", "INHERITED_FROM_SOURCE")
META_ACCOUNT = re.compile(r"\{account\}|act_\d+")
TIKTOK_PATH = re.compile(r"[a-z0-9_]+(/[a-z0-9_]+)*")
TIKTOK_DAILY_MODES = ("BUDGET_MODE_DAY", "BUDGET_MODE_DYNAMIC_DAILY_BUDGET")
# A TikTok POST whose path ends in one of these only reads.
TIKTOK_READ_TAILS = ("get", "list", "search", "estimate", "recommend", "check", "info", "download")
GOOGLE_PATH = re.compile(r"[A-Za-z0-9_.~:/-]+")
# Google Ads custom methods that are sent as POST and change nothing.
GOOGLE_READS = re.compile(r"(search|searchStream|suggest\w*|generate\w+|list\w+)")
# The writes google call may send: conversion uploads and customer-list jobs. Nothing here shapes a campaign.
GOOGLE_WRITES = re.compile(r"(^|/)(customers/[^/:]+:upload\w+|offlineUserDataJobs:create|offlineUserDataJobs/[^/:]+:(addOperations|run))$")
# What serves on its own once its parent is on.
GOOGLE_DELIVERABLES = {"adGroupOperation": "campaign", "assetGroupOperation": "campaign", "adGroupAdOperation": "adGroup"}
GOOGLE_PARENTS = ("campaign", "adGroup", "assetGroup")
ONLY_CREATES = "a launch plan only creates"
# What a launch plan may create: a campaign and the parts that hang under it. Everything else is a single command.
GOOGLE_PLAN_KINDS = {
    "campaignBudgetOperation", "campaignOperation", "campaignCriterionOperation", "campaignAssetOperation",
    "campaignAssetSetOperation", "campaignBidModifierOperation", "campaignLabelOperation",
    "adGroupOperation", "adGroupCriterionOperation", "adGroupAdOperation", "adGroupAssetOperation",
    "adGroupBidModifierOperation", "adGroupLabelOperation", "adGroupAdLabelOperation",
    "assetOperation", "assetSetOperation", "assetSetAssetOperation", "assetGroupOperation", "assetGroupAssetOperation",
    "assetGroupSignalOperation", "assetGroupListingGroupFilterOperation", "audienceOperation", "labelOperation"}
META_PLAN_EDGES = ("campaigns", "adsets", "adcreatives", "ads", "adimages", "advideos")
TIKTOK_PLAN_ROUTES = ("campaign/create", "adgroup/create", "ad/create", "smart_plus/campaign/create",
                      "smart_plus/adgroup/create", "smart_plus/ad/create", "creative/portfolio/create",
                      "campaign/gmv_max/create")


def amount(value, where):
    """A budget as a number. NaN, infinity, a negative value or text would switch every comparison off."""
    number = None
    if not isinstance(value, bool) and isinstance(value, (int, float, str)):
        try:
            number = float(value)
        except ValueError:
            number = None
    if number is None or not math.isfinite(number) or number < 0:
        raise Refused("%s: %r is not a budget: write a plain number that is not negative" % (where, value))
    return number


def daily_ceiling(config):
    """The user's daily ceiling. A missing or zero ceiling is not permission: nothing with a budget is sent without one."""
    value = config.get("guardrails", {}).get("max_daily_budget")
    number = None
    if not isinstance(value, bool) and isinstance(value, (int, float, str)):
        try:
            number = float(value)
        except ValueError:
            number = None
    if number is None or not math.isfinite(number) or number <= 0:
        raise Refused("guardrails.max_daily_budget in ads/config.json is not a positive number (%r)" % (value,),
                      "the user sets the daily ceiling there before anything with a budget is sent")
    return number


def _check_budget(value, config, where):
    limit = daily_ceiling(config)
    if value > limit:
        raise Refused(
            "%s sets a daily budget of %g, above the ceiling of %g" % (where, value, limit),
            "raise guardrails.max_daily_budget in ads/config.json if that is intended")


def _check_total(value, config, where):
    limit = float(config.get("guardrails", {}).get("max_total_budget", 0) or 0)
    if not limit:
        raise Refused(
            "%s sets a lifetime budget of %g, and lifetime budgets are switched off" % (where, value),
            "use a daily budget, or set guardrails.max_total_budget in ads/config.json when the user asks for a lifetime budget")
    if value > limit:
        raise Refused(
            "%s sets a lifetime budget of %g, above the ceiling of %g" % (where, value, limit),
            "raise guardrails.max_total_budget in ads/config.json if that is intended")


def activation_note(summary, activate):
    """What a preview says about a call that would switch delivery on."""
    if summary.get("activates") and not activate:
        return ("this call switches delivery on: sending it needs --activate as well as --yes, "
                "after the user approved the spend")
    return None


# ── Google Ads ───────────────────────────────────────────────────────────

def _camel(key):
    if "_" not in key or key.startswith("@"):
        return key
    head, *rest = key.split("_")
    return head + "".join(part[:1].upper() + part[1:] for part in rest)


def google_canonical(value):
    """A Google Ads body with every field name in lowerCamelCase.

    The API reads campaign_operation exactly like campaignOperation. The rules below
    know one spelling, so the body is rewritten to it, and the rewritten body is what
    gets sent: what was judged and what leaves are the same thing.
    """
    if isinstance(value, dict):
        return {(_camel(key) if isinstance(key, str) else key): google_canonical(item) for key, item in value.items()}
    if isinstance(value, list):
        return [google_canonical(item) for item in value]
    return value


def _own(parent, born_here, plan):
    """True for an object this request or this plan creates; a {{step.field}} reference points at an earlier step."""
    return parent in born_here or parent in plan or "{{" in str(parent)


def google_mutate(body, config, activate=False, plan=None):
    """Judge a googleAds:mutate body. plan: None for a single command, else the resource names earlier steps created.

    The body is read in its camelCase spelling whatever spelling it came in; callers send that same spelling.
    """
    body = google_canonical(body)
    operations = body.get("mutateOperations")
    if not isinstance(operations, list) or not operations:
        raise Refused("a Google mutate body needs a non-empty mutateOperations list")
    summary = {"operations": len(operations), "creates": [], "updates": [], "removes": [], "daily_budgets": [],
               "total_budgets": [], "activates": False}
    # Parents this very request creates: a campaign is forced to be paused, so what hangs under it cannot serve yet.
    born_here = set()
    for operation in operations:
        if isinstance(operation, dict) and len(operation) == 1:
            created = (next(iter(operation.values())) or {}).get("create") or {}
            if isinstance(created, dict) and re.search(r"/-\d+$", str(created.get("resourceName", ""))):
                born_here.add(created["resourceName"])
    for index, operation in enumerate(operations):
        if not isinstance(operation, dict) or len(operation) != 1:
            raise Refused("operation %d must hold exactly one ...Operation key" % index)
        kind, payload = next(iter(operation.items()))
        payload = payload or {}
        create, update = payload.get("create"), payload.get("update")
        if create is not None:
            summary["creates"].append(kind)
        if update is not None:
            summary["updates"].append(kind)
        if payload.get("remove"):
            summary["removes"].append(kind)
        if plan is not None:
            if update is not None or payload.get("remove"):
                raise Refused("operation %d changes or removes an object that already exists, and %s" % (index, ONLY_CREATES),
                              "send that change as a single command, google mutate --file FILE, shown to the user first")
            if kind not in GOOGLE_PLAN_KINDS:
                raise Refused("operation %d creates %s, which is no part of a campaign, and %s campaigns and what hangs "
                              "under them" % (index, kind.replace("Operation", ""), ONLY_CREATES),
                              "send it as a single command, google mutate --file FILE, shown to the user first")
            foreign = [field for field in GOOGLE_PARENTS
                       if isinstance(create, dict) and create.get(field) and not _own(create[field], born_here, plan)]
            if foreign:
                raise Refused("operation %d adds %s to a %s that this plan did not create, and %s"
                              % (index, kind.replace("Operation", ""), foreign[0], ONLY_CREATES),
                              "it would deliver on a budget the plan neither sets nor checks, and no rollback could take it "
                              "back: send it as a single command, google mutate --file FILE, shown to the user first")
        body_part = create if create is not None else update
        if kind == "campaignBudgetOperation" and body_part and body_part.get("amountMicros") is not None:
            value = amount(body_part["amountMicros"], "operation %d" % index) / 1_000_000
            summary["daily_budgets"].append(value)
            _check_budget(value, config, "operation %d" % index)
        if kind == "campaignBudgetOperation" and body_part and body_part.get("totalAmountMicros") is not None:
            value = amount(body_part["totalAmountMicros"], "operation %d" % index) / 1_000_000
            summary["total_budgets"].append(value)
            _check_total(value, config, "operation %d" % index)
        if kind == "campaignOperation" and create is not None and create.get("status") != "PAUSED":
            raise Refused("operation %d creates a campaign with status %r" % (index, create.get("status")),
                          "create the campaign with \"status\": \"PAUSED\" and enable it with launch activate")
        if kind in GOOGLE_DELIVERABLES and create is not None and create.get("status") != "PAUSED":
            parent = create.get(GOOGLE_DELIVERABLES[kind])
            if parent not in born_here:
                summary["activates"] = True
                if not activate:
                    raise Refused(
                        "operation %d creates %s switched on under a %s that already exists, so it could serve at once"
                        % (index, kind.replace("Operation", ""), GOOGLE_DELIVERABLES[kind]),
                        "create it with \"status\": \"PAUSED\" and enable it with launch activate, "
                        "or add --activate if it should serve now")
        # Any status but the two that stop delivery counts as switching on: ENABLED, a number, an unknown word.
        if isinstance(update, dict) and "status" in update and update["status"] not in ("PAUSED", "REMOVED"):
            summary["activates"] = True
            if not activate:
                raise Refused("operation %d switches %s on (status %r)" % (index, kind, update["status"]),
                              "add --activate if spend should start; write a status as its name, PAUSED or ENABLED")
        # A campaign moved onto another budget may spend an amount this request does not show.
        if kind == "campaignOperation" and isinstance(update, dict) and "campaignBudget" in update:
            summary["activates"] = True
            if not activate:
                raise Refused("operation %d moves a campaign onto another budget, whose amount this request does not show"
                              % index, "tell the user the amount of that budget; add --activate once they approved it")
    return summary


def google_call(method, path):
    """What google call may send. Returns "read" or "write"; everything else is refused.

    Every ...:mutate method, batch jobs, recommendations and experiments can create,
    enable or re-budget a campaign without the paused rule and the ceilings, so they
    are not sent from here at all.
    """
    method, path = str(method).upper(), str(path).strip("/")
    if not path or not GOOGLE_PATH.fullmatch(path) or "//" in path or ".." in path:
        raise Refused("the path %r is not a plain Google Ads API path" % path,
                      "write it without a query string; parameters go into --data")
    verb = path.rsplit(":", 1)[1] if ":" in path.rsplit("/", 1)[-1] else ""
    if method == "GET" and not verb:
        return "read"
    if method in ("GET", "POST") and GOOGLE_READS.fullmatch(verb):
        return "read"
    if method == "POST" and GOOGLE_WRITES.search(path):
        return "write"
    raise Refused(
        "google call sends reads and conversion uploads only, not %s %s" % (method, path),
        "campaigns, budgets, ad groups, ads, keywords and assets are changed with google mutate, "
        "where the paused rule and the budget ceilings apply")


# ── Meta ─────────────────────────────────────────────────────────────────

def meta_path(path):
    """A Graph API path as the guard rails need it: plain segments, no parameters inside."""
    route = str(path).strip("/")
    if not route or not META_PATH.fullmatch(route) or ".." in route:
        raise Refused("the path %r is not a plain Graph API path" % path,
                      "parameters go into -p KEY=VALUE or into the params of the step, never into the path")
    return route


def _no_method(params, what):
    """The Graph API lets a parameter named method turn one kind of request into another, a GET into a DELETE."""
    for key in params or {}:
        # method, _method, Method, %6dethod, X-HTTP-Method-Override: every disguise of the same order
        name = re.sub(r"[^a-z]", "", urllib.parse.unquote(str(key)).lower())
        if name in ("method", "httpmethod", "methodoverride", "httpmethodoverride", "xhttpmethodoverride"):
            raise Refused("a parameter named method would turn this %s into another kind of request" % what,
                          "use the command for the request you mean: meta post or meta delete, shown to the user first")


def meta_read(path, params=None):
    """A Graph API read that stays a read: a plain path and no method parameter."""
    route = meta_path(path)
    _no_method(params, "read")
    return route


def meta_request(method, path, params, config, activate=False, plan=False):
    """A Graph API write: POST to an edge creates, POST to an object id updates."""
    params = params or {}
    route = meta_path(path)
    _no_method(params, "call")
    segments = route.split("/")
    edge = segments[-1]
    if plan and (len(segments) != 2 or not META_ACCOUNT.fullmatch(segments[0])):
        raise Refused("this step writes to %s, an object that already exists, and %s" % (route, ONLY_CREATES),
                      "send that change as a single command, meta post PATH, shown to the user first")
    if plan and edge not in META_PLAN_EDGES:
        raise Refused("this step writes to %s, which is no part of a campaign, and %s campaigns and what hangs under them"
                      % (route, ONLY_CREATES), "send it as a single command, meta post PATH, shown to the user first")
    hidden = [key for key in META_CONTAINERS if key in params]
    if hidden or "batch" in edge.lower() or "async" in edge.lower():
        raise Refused("%s holds other calls or a second object, where the guard rails cannot read status and budget"
                      % (hidden[0] if hidden else edge),
                      "send each object as its own call or its own step")
    creates = method == "POST" and edge in META_CREATE_EDGES
    status = params.get("status")
    summary = {"creates": edge if creates else None, "activates": False, "daily_budget": None, "total_budget": None}
    if creates and status != "PAUSED":
        raise Refused("%s would be created with status %r" % (edge, status),
                      "create it with status=PAUSED and enable it with launch activate")
    switches_on = any(str(params.get(key, "")).upper() in META_ON for key in ("status", "configured_status"))
    if method == "POST" and edge == "copies" and params.get("status_option") != "PAUSED":
        switches_on = True
    if method == "POST" and edge == "adrules_library":
        # An automated rule acts later on its own: it can enable ads or change budgets with nobody approving that step.
        summary["activates"] = True
        if not activate:
            raise Refused("an automated rule can switch ads on or change budgets later, with nobody approving that step",
                          "create it in Ads Manager, or add --activate after the user approved exactly this rule")
    if method == "POST" and switches_on:
        summary["activates"] = True
        if not activate:
            if edge == "copies":
                raise Refused("a copy would not be created paused (status_option=%r)" % params.get("status_option"),
                              "send status_option=PAUSED, or add --activate if the copy should deliver at once")
            raise Refused("this call sets an active status", "add --activate if spend should start")
    currency = str(config.get("project", {}).get("currency", "USD")).upper()
    minor = 1 if currency in ZERO_DECIMAL else 100
    if params.get("daily_budget") not in (None, ""):
        value = amount(params["daily_budget"], edge) / minor
        summary["daily_budget"] = value
        _check_budget(value, config, edge)
    if params.get("lifetime_budget") not in (None, ""):
        value = amount(params["lifetime_budget"], edge) / minor
        summary["total_budget"] = value
        _check_total(value, config, edge)
    return summary


# ── TikTok ───────────────────────────────────────────────────────────────

def tiktok_path(path):
    route = str(path).strip("/")
    if not route or not TIKTOK_PATH.fullmatch(route):
        raise Refused("the path %r is not a plain TikTok Marketing API path" % path,
                      "write it as in the documentation, for example campaign/create/; parameters go into the body")
    return route


def _statuses(value):
    found = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "operation_status":
                found.append(item)
            else:
                found.extend(_statuses(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(_statuses(item))
    return found


def tiktok_request(path, body, config, activate=False, plan=False):
    body = body or {}
    route = tiktok_path(path)
    parts = route.split("/")
    summary = {"creates": None, "activates": False, "daily_budget": None, "total_budget": None}
    is_create = parts[-1] == "create"
    reads = parts[-1] in TIKTOK_READ_TAILS
    if plan and not reads and route not in TIKTOK_PLAN_ROUTES:
        raise Refused("this step sends %s, which is no part of a new campaign, and %s campaigns and what hangs under them"
                      % (route, ONLY_CREATES),
                      "send it as a single command, tiktok post PATH --data @FILE, shown to the user first")
    if route.startswith("optimizer/rule") and not reads:
        # An automated rule acts later on its own, like a Meta rule.
        summary["activates"] = True
        if not activate:
            raise Refused("an automated rule can switch ads on or change budgets later, with nobody approving that step",
                          "create it in TikTok Ads Manager, or add --activate after the user approved exactly this rule")
    level = next((p for p in reversed(parts[:-1]) if p in ("campaign", "adgroup", "ad", "gmv_max")), None)
    if is_create and level == "gmv_max":
        # campaign/gmv_max/create/ has no status field, so the campaign cannot be born paused.
        summary["creates"], summary["activates"] = "gmv_max", True
        if not activate:
            raise Refused("a GMV Max campaign cannot be created paused: TikTok offers no status field on this call",
                          "add --activate to accept that delivery may start at once, "
                          "then pause it with campaign/status/update/ if it should wait")
    elif is_create and level in ("campaign", "adgroup", "ad"):
        summary["creates"] = level
        # The status counts only where TikTok reads it: at the top of the body, and for the manual ad/create/,
        # which makes one ad per entry of creatives, on every entry.
        creatives = body.get("creatives") if isinstance(body.get("creatives"), list) else []
        if level == "ad" and parts[0] != "smart_plus" and creatives:
            covered = all(isinstance(item, dict) and item.get("operation_status") == "DISABLE" for item in creatives)
        else:
            covered = body.get("operation_status") == "DISABLE"
        if not covered or any(s != "DISABLE" for s in _statuses(body)):
            raise Refused("%s would be created switched on" % route,
                          "send \"operation_status\": \"DISABLE\" and enable it with launch activate")
    if not is_create and "ENABLE" in _statuses(body):
        summary["activates"] = True
        if not activate:
            raise Refused("this call sets operation_status=ENABLE", "add --activate if spend should start")
    budget = body.get("budget")
    if isinstance(budget, list) and route.endswith("budget/update"):
        # adgroup/budget/update/ takes one entry per ad group.
        values = [amount(item.get("budget") if isinstance(item, dict) else item, route) for item in budget]
        for value in values:
            _check_budget(value, config, route)
        summary["daily_budget"] = max(values) if values else None
    elif budget not in (None, "") and body.get("budget_mode", TIKTOK_DAILY_MODES[0]) in TIKTOK_DAILY_MODES:
        value = amount(budget, route)
        summary["daily_budget"] = value
        _check_budget(value, config, route)
    elif budget not in (None, "") and body.get("budget_mode") == "BUDGET_MODE_TOTAL":
        value = amount(budget, route)
        summary["total_budget"] = value
        _check_total(value, config, route)
    elif budget not in (None, ""):
        amount(budget, route)
    return summary
