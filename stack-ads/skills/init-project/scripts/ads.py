#!/usr/bin/env python3
"""ads.py: the command-line toolkit of the stack-ads plugin.

Research, creative generation, guarded campaign launch and reporting for
Google Ads, Meta and TikTok. Python 3.9+, standard library only.

A command that changes something outside the project prints what it would do
and stops unless it carries --yes; starting spend also needs --activate.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from adskit import __version__, creative, google, keys, launch, meta, recon, tiktok, workspace  # noqa: E402
from adskit.core import (AdsError, Context, EXIT_USAGE, Refused, emit, find_workspace, load_json_arg,  # noqa: E402
                         parse_pairs, redact)


def add_output(parser, csv=False):
    if csv:
        parser.add_argument("--format", choices=("json", "csv"), default="json")
    parser.add_argument("--out", help="save the result to this file instead of printing it")


def add_write(parser, activate=False):
    parser.add_argument("--yes", action="store_true", help="really send the write (default: dry run)")
    if activate:
        parser.add_argument("--activate", action="store_true", help="allow the call to switch delivery on")


def add_params(parser):
    parser.add_argument("-p", "--param", action="append", default=[], metavar="KEY=VALUE", help="request parameter, repeatable")


class Parser(argparse.ArgumentParser):
    """No abbreviated flags: --y must never be read as --yes, nor --act as --activate."""

    def __init__(self, *args, **kwargs):
        kwargs["allow_abbrev"] = False
        super().__init__(*args, **kwargs)


def build_parser():
    parser = Parser(prog="ads.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action="version", version="stack-ads toolkit %s" % __version__)
    parser.add_argument("--dir", help="ads workspace (default: the folder holding this toolkit, else ./ads)")
    groups = parser.add_subparsers(dest="group", required=True, metavar="COMMAND")

    p = groups.add_parser("init", help="create the workspace and copy the toolkit into it")
    p.add_argument("--dir", default=argparse.SUPPRESS)
    p.add_argument("--update", action="store_true", help="refresh only the toolkit copy")

    p = groups.add_parser("keys", help="list every variable and whether it is set")
    p.add_argument("--json", action="store_true")

    p = groups.add_parser("doctor", help="check the keys; with --live make one read-only call per service")
    p.add_argument("--live", action="store_true")
    p.add_argument("--only", help="comma list of services")
    p.add_argument("--json", action="store_true")

    sub = groups.add_parser("env", help="hand the keys to Claude Code").add_subparsers(dest="command", required=True)
    p = sub.add_parser("sync-claude", help="copy ads/.env into .claude/settings.local.json")
    p.add_argument("--settings")

    # Google Ads
    sub = groups.add_parser("google", help="Google Ads API").add_subparsers(dest="command", required=True)
    p = sub.add_parser("login", help="print the consent URL, or exchange the pasted redirect URL")
    p.add_argument("--port", type=int, default=8080)
    p.add_argument("--scopes", default="ads,gsc")
    p.add_argument("--redirect-url")
    p = sub.add_parser("import-adc", help="take the credentials gcloud stored")
    p.add_argument("--file")
    p = sub.add_parser("export-adc", help="write the credentials file the google-ads MCP server reads")
    p.add_argument("--file")
    sub.add_parser("customers", help="list reachable accounts")
    p = sub.add_parser("search", help="run a GAQL query")
    p.add_argument("--query", required=True)
    p.add_argument("--customer")
    add_output(p, csv=True)
    p = sub.add_parser("mutate", help="send a googleAds:mutate body (validation only without --yes)")
    p.add_argument("--file", required=True)
    p.add_argument("--customer")
    p.add_argument("--partial-failure", action="store_true")
    add_write(p, activate=True)
    p = sub.add_parser("keyword-ideas", help="Keyword Planner ideas")
    p.add_argument("--keywords")
    p.add_argument("--url")
    p.add_argument("--geo", default="")
    p.add_argument("--language", default="")
    p.add_argument("--limit", type=int, default=100)
    p.add_argument("--customer")
    add_output(p, csv=True)
    p = sub.add_parser("geo", help="resolve place names to geo target constants")
    p.add_argument("--query", required=True)
    p.add_argument("--country")
    p.add_argument("--locale", default="en")
    p = sub.add_parser("call", help="a read or a conversion upload by its REST path")
    p.add_argument("method")
    p.add_argument("path")
    p.add_argument("--data")
    add_write(p)
    add_output(p)

    sub = groups.add_parser("gsc", help="Search Console API").add_subparsers(dest="command", required=True)
    sub.add_parser("sites", help="list verified properties")
    p = sub.add_parser("query", help="Search Analytics rows")
    p.add_argument("--site")
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--dimensions", default="query")
    p.add_argument("--row-limit", type=int, default=1000)
    p.add_argument("--type", default="web")
    p.add_argument("--data-state", choices=("final", "all"), default="final")
    p.add_argument("--filter", action="append", default=[], metavar="DIM:OP:VALUE")
    add_output(p, csv=True)

    # Meta
    sub = groups.add_parser("meta", help="Meta Marketing API").add_subparsers(dest="command", required=True)
    p = sub.add_parser("get", help="Graph API read")
    p.add_argument("path")
    add_params(p)
    add_output(p)
    p = sub.add_parser("post", help="Graph API write (dry run without --yes)")
    p.add_argument("path")
    add_params(p)
    p.add_argument("--data")
    add_write(p, activate=True)
    p = sub.add_parser("delete", help="Graph API delete")
    p.add_argument("path")
    add_write(p)
    p = sub.add_parser("upload-image", help="upload to the ad image library")
    p.add_argument("--file", required=True)
    add_write(p)
    p = sub.add_parser("upload-video", help="upload to the ad video library")
    p.add_argument("--file", required=True)
    p.add_argument("--name")
    add_write(p)
    p = sub.add_parser("insights", help="performance rows")
    p.add_argument("--object")
    p.add_argument("--level", choices=("account", "campaign", "adset", "ad"), default="campaign")
    p.add_argument("--preset")
    p.add_argument("--since")
    p.add_argument("--until")
    p.add_argument("--fields")
    p.add_argument("--breakdowns")
    add_params(p)
    add_output(p, csv=True)
    p = sub.add_parser("search", help="targeting search")
    p.add_argument("--type", required=True)
    p.add_argument("--q")
    add_params(p)
    p = sub.add_parser("ad-library", help="Ad Library API search")
    p.add_argument("--terms", required=True)
    p.add_argument("--countries", required=True)
    p.add_argument("--limit", type=int, default=50)
    add_output(p)

    # TikTok
    sub = groups.add_parser("tiktok", help="TikTok Marketing API").add_subparsers(dest="command", required=True)
    p = sub.add_parser("get", help="Marketing API read")
    p.add_argument("path")
    add_params(p)
    add_output(p)
    p = sub.add_parser("post", help="Marketing API write (dry run without --yes)")
    p.add_argument("path")
    p.add_argument("--data", required=True)
    add_write(p, activate=True)
    p = sub.add_parser("upload-video", help="upload a video creative")
    p.add_argument("--file")
    p.add_argument("--url")
    p.add_argument("--name")
    add_write(p)
    p = sub.add_parser("upload-image", help="upload an image creative")
    p.add_argument("--file", required=True)
    add_write(p)
    p = sub.add_parser("report", help="integrated report")
    p.add_argument("--level", required=True)
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--metrics")
    p.add_argument("--dimensions")
    add_output(p, csv=True)
    p = sub.add_parser("oauth-exchange", help="trade an authorization code for a long-term token")
    p.add_argument("--auth-code", required=True)
    p.add_argument("--write", action="store_true")

    # Creative generation
    p = groups.add_parser("models", help="list or pick generation models")
    p.add_argument("--provider", choices=creative.PROVIDERS)
    p.add_argument("--kind", choices=creative.KINDS)
    p.add_argument("--query")
    p.add_argument("--pick", action="store_true")
    p.add_argument("--json", action="store_true")
    p = groups.add_parser("image", help="generate images")
    p.add_argument("--prompt", required=True)
    p.add_argument("--provider", choices=creative.SUPPORT["image"])
    p.add_argument("--model")
    p.add_argument("--aspect")
    p.add_argument("--size", help="WIDTHxHEIGHT")
    p.add_argument("--n", type=int, default=1)
    p.add_argument("--quality", choices=("low", "medium", "high"))
    p.add_argument("--ref", action="append", default=[], help="reference image, repeatable")
    p.add_argument("--transparent", action="store_true")
    p.add_argument("--fit", help="also save a copy scaled and cropped to WIDTHxHEIGHT (needs ffmpeg)")
    p.add_argument("--out")
    p.add_argument("--name")
    p = groups.add_parser("video", help="generate a short clip")
    p.add_argument("--prompt", required=True)
    p.add_argument("--provider", choices=creative.SUPPORT["video"])
    p.add_argument("--model")
    p.add_argument("--aspect", default="9:16")
    p.add_argument("--seconds", type=int, default=8)
    p.add_argument("--resolution", default="720p")
    p.add_argument("--image", help="first frame")
    p.add_argument("--out")
    p.add_argument("--name")
    p = groups.add_parser("speech", help="generate a voice-over")
    p.add_argument("--text", required=True)
    p.add_argument("--provider", choices=creative.SUPPORT["speech"])
    p.add_argument("--model")
    p.add_argument("--voice")
    p.add_argument("--out")
    p = groups.add_parser("music", help="generate a music track")
    p.add_argument("--prompt", required=True)
    p.add_argument("--provider", choices=creative.SUPPORT["music"])
    p.add_argument("--model")
    p.add_argument("--out")
    p = groups.add_parser("analyze", help="describe an image or a video")
    p.add_argument("--prompt", required=True)
    p.add_argument("--file")
    p.add_argument("--url")
    p.add_argument("--provider", choices=creative.SUPPORT["analysis"])
    p.add_argument("--model")

    sub = groups.add_parser("fal", help="any fal.ai model").add_subparsers(dest="command", required=True)
    p = sub.add_parser("schema", help="input fields of a model")
    p.add_argument("model")
    p = sub.add_parser("run", help="run a model through the queue")
    p.add_argument("model")
    p.add_argument("--input", required=True)
    p.add_argument("--out")
    p.add_argument("--name")

    # Research
    sub = groups.add_parser("firecrawl", help="scrape, search, map").add_subparsers(dest="command", required=True)
    p = sub.add_parser("scrape")
    p.add_argument("url")
    p.add_argument("--formats", default="markdown")
    p.add_argument("--schema")
    p.add_argument("--prompt")
    add_output(p)
    p = sub.add_parser("search")
    p.add_argument("query")
    p.add_argument("--limit", type=int, default=10)
    add_output(p)
    p = sub.add_parser("map")
    p.add_argument("url")
    p.add_argument("--limit", type=int, default=200)
    p.add_argument("--search")
    add_output(p)

    sub = groups.add_parser("apify", help="run Apify Actors").add_subparsers(dest="command", required=True)
    p = sub.add_parser("actor", help="pricing and input fields of an Actor")
    p.add_argument("actor")
    p = sub.add_parser("run", help="run an Actor with a spend cap")
    p.add_argument("actor")
    p.add_argument("--input", required=True)
    p.add_argument("--max-usd", type=float)
    p.add_argument("--max-items", type=int)
    p.add_argument("--timeout", type=int, default=900)
    add_output(p)

    sub = groups.add_parser("dataforseo", help="DataForSEO v3").add_subparsers(dest="command", required=True)
    p = sub.add_parser("post")
    p.add_argument("path")
    p.add_argument("--data", required=True)
    p.add_argument("--sandbox", action="store_true")
    add_output(p)
    p = sub.add_parser("get")
    p.add_argument("path")
    p.add_argument("--sandbox", action="store_true")
    add_output(p)

    # Launch
    sub = groups.add_parser("launch", help="launch plans").add_subparsers(dest="command", required=True)
    for name, text in (("plan", "dry run: print the eight blocks"), ("apply", "create everything, paused"),
                       ("status", "read back what the plan created"), ("activate", "enable what the plan created"),
                       ("rollback", "pause, or with --remove delete, what the plan created")):
        p = sub.add_parser(name, help=text)
        p.add_argument("--file", required=True)
        if name in ("apply", "activate", "rollback"):
            p.add_argument("--yes", action="store_true")
        if name == "rollback":
            p.add_argument("--remove", action="store_true")
        if name == "apply":
            p.add_argument("--resend", action="append", default=[], metavar="STEP",
                           help="send again a step that ended without a clear answer, after checking the ad account")
    p = groups.add_parser("ledger", help="show what was applied")
    p.add_argument("--plan")
    p.add_argument("--json", action="store_true")
    return parser


def run(args):
    if args.group == "init":
        return emit(workspace.init(getattr(args, "dir", None) or "ads", update=args.update))
    ctx = Context(find_workspace(args.dir))
    group, command = args.group, getattr(args, "command", None)

    if group == "keys":
        rows = keys.table(ctx)
        if args.json:
            return emit(rows)
        for row in rows:
            print("%-11s %-32s %-8s %s" % (row["service"], row["variable"], "set" if row["set"] else "missing",
                                           "" if row["needed"] else "(optional)"))
        return None
    if group == "doctor":
        rows = keys.doctor(ctx, live=args.live, only=args.only)
        return emit(rows) if args.json else print(redact(keys.render(rows)), end="")
    if group == "env":
        return emit(workspace.sync_claude(ctx, args.settings))

    if group == "google":
        if command == "login":
            if args.redirect_url:
                return emit(google.login_exchange(ctx, args.redirect_url, args.port))
            print("Open this address, sign in with the Google account that manages the ads, and allow access:\n")
            print(google.login_url(ctx, args.port, args.scopes))
            print("\nThe browser ends on an address starting with http://localhost:%d (the page may fail to load: that is "
                  "expected). Copy that whole address and run:\n  python3 ads/tools/ads.py google login --redirect-url "
                  "'PASTED_ADDRESS'" % args.port)
            return None
        if command == "import-adc":
            return emit(google.import_adc(ctx, args.file))
        if command == "export-adc":
            return emit(google.export_adc(ctx, args.file))
        if command == "customers":
            return emit(google.customers(ctx))
        if command == "search":
            return emit(google.search(ctx, args.query, args.customer), args.format, args.out)
        if command == "mutate":
            out = google.mutate(ctx, load_json_arg("@" + args.file), customer=args.customer, yes=args.yes,
                                activate=args.activate, partial_failure=args.partial_failure, preview=True)
            emit(out)
            if out.get("partial_failure"):
                raise AdsError("Google applied only part of the request: %s" % out["partial_failure"],
                               "the output above names what was created; the operations that failed were not applied")
            return None
        if command == "keyword-ideas":
            return emit(google.keyword_ideas(ctx, args.keywords, args.url, args.geo, args.language, args.limit, args.customer),
                        args.format, args.out)
        if command == "geo":
            return emit(google.geo(ctx, args.query, args.country, args.locale))
        if command == "call":
            return emit(google.call(ctx, args.method, args.path, load_json_arg(args.data), yes=args.yes), "json", args.out)
    if group == "gsc":
        if command == "sites":
            return emit(google.gsc_sites(ctx))
        return emit(google.gsc_query(ctx, args.site, args.start, args.end, args.dimensions, args.row_limit, args.type,
                                     args.filter, args.data_state), args.format, args.out)

    if group == "meta":
        if command == "get":
            return emit(meta.get(ctx, args.path, parse_pairs(args.param)), "json", args.out)
        if command == "post":
            params = dict(load_json_arg(args.data) or {})
            params.update(parse_pairs(args.param))
            return emit(meta.post(ctx, args.path, params, yes=args.yes, activate=args.activate, preview=True))
        if command == "delete":
            return emit(meta.delete(ctx, args.path, yes=args.yes))
        if command == "upload-image":
            return emit(meta.upload_image(ctx, args.file, yes=args.yes))
        if command == "upload-video":
            return emit(meta.upload_video(ctx, args.file, args.name, yes=args.yes))
        if command == "insights":
            return emit(meta.insights(ctx, args.object, args.level, args.preset, args.since, args.until, args.fields,
                                      args.breakdowns, parse_pairs(args.param)), args.format, args.out)
        if command == "search":
            return emit(meta.search(ctx, args.type, args.q, parse_pairs(args.param)))
        if command == "ad-library":
            return emit(meta.ad_library(ctx, args.terms, args.countries, args.limit), "json", args.out)

    if group == "tiktok":
        if command == "get":
            return emit(tiktok.get(ctx, args.path, parse_pairs(args.param)), "json", args.out)
        if command == "post":
            return emit(tiktok.post(ctx, args.path, load_json_arg(args.data), yes=args.yes, activate=args.activate,
                                    preview=True))
        if command == "upload-video":
            return emit(tiktok.upload_video(ctx, args.file, args.url, args.name, yes=args.yes))
        if command == "upload-image":
            return emit(tiktok.upload_image(ctx, args.file, yes=args.yes))
        if command == "report":
            return emit(tiktok.report(ctx, args.level, args.start, args.end, args.metrics, args.dimensions), args.format, args.out)
        if command == "oauth-exchange":
            return emit(tiktok.oauth_exchange(ctx, args.auth_code, write=args.write))

    if group == "models":
        providers = [args.provider] if args.provider else [p for p in creative.PROVIDERS
                                                           if ctx.key(creative.PROVIDER_KEYS[p], required=False)]
        if not providers:
            ctx.key("GEMINI_API_KEY")
        if args.pick:
            picked = {}
            for kind in ([args.kind] if args.kind else creative.KINDS):
                for provider in providers:
                    if provider in creative.SUPPORT[kind] and not (provider == "openai" and kind == "analysis"):
                        try:
                            picked[kind] = {"provider": provider, "model": creative.pick(ctx, provider, kind, save=True)}
                            break
                        except AdsError as exc:
                            picked[kind] = {"provider": provider, "error": exc.message}
            return emit({"saved_in": "ads/config.json", "models": picked})
        rows = []
        for provider in providers:
            rows.extend(creative.list_models(ctx, provider, args.kind, args.query))
        if args.json:
            return emit(rows)
        for row in rows:
            print("%-7s %-9s %-52s %s" % (row["provider"], row["kind"], row["id"], row.get("name") or ""))
        return None
    if group == "image":
        return emit(creative.image(ctx, args.prompt, args.provider, args.model, args.aspect, args.size, args.n, args.quality,
                                   args.ref, args.transparent, args.out, args.name, args.fit))
    if group == "video":
        return emit(creative.video(ctx, args.prompt, args.provider, args.model, args.aspect, args.seconds, args.resolution,
                                   args.image, args.out, args.name))
    if group == "speech":
        return emit(creative.speech(ctx, args.text, args.provider, args.model, args.voice, args.out))
    if group == "music":
        return emit(creative.music(ctx, args.prompt, args.provider, args.model, args.out))
    if group == "analyze":
        return emit(creative.analyze(ctx, args.prompt, args.file, args.url, args.provider, args.model))
    if group == "fal":
        if command == "schema":
            return emit(creative.fal_schema(ctx, args.model))
        return emit(creative.fal_run(ctx, args.model, load_json_arg(args.input), args.out, args.name))

    if group == "firecrawl":
        if command == "scrape":
            data = recon.firecrawl_scrape(ctx, args.url, args.formats, load_json_arg(args.schema), args.prompt)
        elif command == "search":
            data = recon.firecrawl_search(ctx, args.query, args.limit)
        else:
            data = recon.firecrawl_map(ctx, args.url, args.limit, args.search)
        return emit(data, "json", args.out)
    if group == "apify":
        if command == "actor":
            return emit(recon.apify_actor(ctx, args.actor))
        result = recon.apify_run(ctx, args.actor, load_json_arg(args.input), args.max_usd, args.max_items, args.timeout)
        if args.out:
            emit(result["items"], "json", args.out)
            return emit({"run_id": result["run_id"], "usage_usd": result["usage_usd"], "items": len(result["items"])})
        return emit(result)
    if group == "dataforseo":
        body = load_json_arg(args.data) if command == "post" else None
        return emit(recon.dataforseo(ctx, command.upper(), args.path, body, args.sandbox), "json", args.out)

    if group == "launch":
        if command == "plan":
            text, problems = launch.plan(ctx, args.file)
            print(redact(text), end="")
            return EXIT_USAGE if problems else None
        if command == "apply":
            return print(redact(launch.apply(ctx, args.file, yes=args.yes, resend=args.resend)), end="")
        if command == "status":
            return emit(launch.status(ctx, args.file))
        if command == "activate":
            return print(redact(launch.activate(ctx, args.file, yes=args.yes)), end="")
        if command == "rollback":
            return print(redact(launch.rollback(ctx, args.file, remove=args.remove, yes=args.yes)), end="")
    if group == "ledger":
        rows = launch.ledger(ctx, args.plan)
        if args.json:
            return emit(rows)
        for row in rows:
            event = row.get("event")
            made = ", ".join("%s %s" % (e["type"], e["id"]) for e in row.get("entities", []))
            if event == "dry-run":
                made = "clean" if row.get("ok") else "%d problem(s)" % row.get("problems", 0)
            elif event == "removed":
                made = "%s %s" % (row.get("type"), row.get("id"))
            elif event == "sending":
                made = "sent; the next line of this step is its answer"
            elif event == "step" and not row.get("ok"):
                made = ("no clear answer: " if row.get("uncertain") else "failed: ") + str(row.get("error", ""))
            print("%s  %-10s %-18s %-12s %s" % (row.get("ts"), event, row.get("plan"), row.get("step", ""), made))
        return None
    raise Refused("unknown command")


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        code = run(args)
        return code if isinstance(code, int) else 0
    except AdsError as exc:
        print("error: %s" % redact(exc.message), file=sys.stderr)
        if exc.hint:
            print("hint: %s" % redact(exc.hint), file=sys.stderr)
        return exc.code
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
