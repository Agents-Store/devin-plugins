#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared language resolution and tool-output catalogue for the macstack-dev scripts.

Why this exists: docs.language governed what the DOCUMENTS said, while every script in
the plugin printed its own output in Russian regardless — including `render.py --check`,
whose output lint reads. A German project got German documents and Russian diagnostics.

Resolution order: explicit --lang → docs.language in macstack.json → MACSTACK_LANG in the
environment → 'en'. An unknown language falls back to English rather than failing: a
missing translation must never stop a render.

Import from anywhere under skills/*/references/:

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from i18n import doc_lang, msg
"""
import os, io, json

DEFAULT = 'en'
SUPPORTED = ('en', 'ru', 'de', 'uk')


def spec_path(macstack_dir):
    """<dir>/macstack.json, falling back to a legacy ./macstack.json beside it."""
    p = os.path.join(macstack_dir, 'macstack.json')
    if os.path.exists(p):
        return p
    legacy = os.path.join(os.path.dirname(os.path.abspath(macstack_dir)), 'macstack.json')
    return legacy if os.path.exists(legacy) else p


def load_spec(macstack_dir):
    p = spec_path(macstack_dir)
    try:
        with io.open(p, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def doc_lang(macstack_dir, override=None):
    """The language the documents' prose is written in."""
    if override:
        return override if override in SUPPORTED else DEFAULT
    spec = load_spec(macstack_dir)
    lang = (spec.get('docs') or {}).get('language') or os.environ.get('MACSTACK_LANG') or DEFAULT
    lang = str(lang).split('-')[0].lower()
    return lang if lang in SUPPORTED else DEFAULT


# --------------------------------------------------------------- tool output
# Keys are stable ASCII ids. Every catalogue falls back to 'en' key by key, so a
# partially translated language degrades to English per string instead of crashing.
CAT = {
    'en': {
        'dry_run':        'dry run — nothing written',
        'applied':        'applied',
        'wrote':          'wrote {path}',
        'unchanged':      '{path} unchanged',
        'would_write':    'would write {path}',
        'refuse_exists':  'refusing to overwrite {path} — pass --force to replace it',
        'no_spec':        'no macstack.json under {dir}',
        'no_folder':      'no macstack/ folder at {dir}',
        'drift':          'DIFFERS from its source: {path}',
        'drift_hint':     'either the file was edited by hand or the source moved and nobody re-rendered',
        'in_sync':        'in sync with its source: {path}',
        'cases_total':    '=== CASES: {n} ===',
        'cases_planned':  'already planned: {n}',
        'cases_audited':  'confirmed by audit: {n}',
        'cases_partial':  'audit found partial or blocked: {n}',
        'cases_open':     'NOT planned and NOT checked: {n}',
        'cases_await':    'awaiting the client, NOT a task: {n}',
        'emit_hint':      'run again with --emit to print task skeletons for these',
        'sections':       'sections',
        'entities':       'entities',
        'table_over':     'table over budget: {where} — {cols} columns, longest cell {chars} chars',
        'lang_off':       'language: {ratio:.0%} of prose is not {lang}',
        'summary_ok':     'OK',
        'summary_warn':   '{n} warnings',
        'summary_err':    '{n} errors',
        'usage':          'usage: {usage}',
    },
    'ru': {
        'dry_run':        'сухой прогон — ничего не записано',
        'applied':        'применено',
        'wrote':          'записан {path}',
        'unchanged':      '{path} без изменений',
        'would_write':    'был бы записан {path}',
        'refuse_exists':  'отказ перезаписать {path} — передайте --force, чтобы заменить',
        'no_spec':        'нет macstack.json в {dir}',
        'no_folder':      'нет папки macstack/ по пути {dir}',
        'drift':          'РАСХОЖДЕНИЕ с источником: {path}',
        'drift_hint':     'либо файл правили руками, либо источник изменился и никто не пересобрал',
        'in_sync':        'совпадает с источником: {path}',
        'cases_total':    '=== КЕЙСОВ: {n} ===',
        'cases_planned':  'уже запланировано: {n}',
        'cases_audited':  'подтверждено аудитом: {n}',
        'cases_partial':  'аудит нашёл частично или заблокировано: {n}',
        'cases_open':     'НЕ запланировано и НЕ проверено: {n}',
        'cases_await':    'ждёт ответа клиента, в задачи НЕ идёт: {n}',
        'emit_hint':      'запустите ещё раз с --emit, чтобы получить скелеты задач',
        'sections':       'разделов',
        'entities':       'сущностей',
        'table_over':     'таблица вне бюджета: {where} — колонок {cols}, длиннейшая ячейка {chars} символов',
        'lang_off':       'язык: {ratio:.0%} прозы не на {lang}',
        'summary_ok':     'ОК',
        'summary_warn':   'предупреждений: {n}',
        'summary_err':    'ошибок: {n}',
        'usage':          'использование: {usage}',
    },
    'de': {
        'dry_run':        'Probelauf — nichts geschrieben',
        'applied':        'angewendet',
        'wrote':          '{path} geschrieben',
        'unchanged':      '{path} unverändert',
        'would_write':    'würde {path} schreiben',
        'refuse_exists':  '{path} wird nicht überschrieben — mit --force ersetzen',
        'no_spec':        'keine macstack.json unter {dir}',
        'no_folder':      'kein macstack/-Ordner unter {dir}',
        'drift':          'WEICHT von der Quelle ab: {path}',
        'drift_hint':     'entweder von Hand bearbeitet, oder die Quelle hat sich geändert',
        'in_sync':        'stimmt mit der Quelle überein: {path}',
        'cases_total':    '=== FÄLLE: {n} ===',
        'cases_planned':  'bereits geplant: {n}',
        'cases_audited':  'durch Audit bestätigt: {n}',
        'cases_partial':  'Audit: teilweise oder blockiert: {n}',
        'cases_open':     'NICHT geplant und NICHT geprüft: {n}',
        'cases_await':    'wartet auf den Kunden, KEINE Aufgabe: {n}',
        'emit_hint':      'erneut mit --emit ausführen für Aufgabenskelette',
    },
    'uk': {
        'dry_run':        'сухий прогін — нічого не записано',
        'applied':        'застосовано',
        'wrote':          'записано {path}',
        'unchanged':      '{path} без змін',
        'would_write':    'було б записано {path}',
        'refuse_exists':  'відмова перезаписати {path} — передайте --force',
        'no_spec':        'немає macstack.json у {dir}',
        'no_folder':      'немає теки macstack/ за шляхом {dir}',
        'drift':          'РОЗБІЖНІСТЬ із джерелом: {path}',
        'drift_hint':     'або файл правили руками, або джерело змінилося і ніхто не перезібрав',
        'in_sync':        'збігається з джерелом: {path}',
        'cases_total':    '=== КЕЙСІВ: {n} ===',
        'cases_planned':  'уже заплановано: {n}',
        'cases_audited':  'підтверджено аудитом: {n}',
        'cases_partial':  'аудит знайшов частково або заблоковано: {n}',
        'cases_open':     'НЕ заплановано і НЕ перевірено: {n}',
        'cases_await':    'чекає на відповідь клієнта, у задачі НЕ йде: {n}',
        'emit_hint':      'запустіть ще раз із --emit, щоб отримати скелети задач',
    },
}


def msg(lang, key, **kw):
    """One tool-output string. Falls back to English per key, never raises on a
    missing translation — a untranslated diagnostic is worth more than a crash."""
    table = CAT.get(lang) or {}
    s = table.get(key) or CAT[DEFAULT].get(key) or key
    try:
        return s.format(**kw)
    except (KeyError, IndexError, ValueError):
        return s


def out(lang, key, **kw):
    print(msg(lang, key, **kw))
