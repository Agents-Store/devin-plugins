#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check the plugin against itself.

Every defect in the 2026-08-25 audit was a claim the plugin made about its own contents
that nothing verified: a document declared `generated` with no generator, a command
routing to an empty skill directory, a deleted document still named in three files, a
README claiming 18 skills of 22, two manifests disagreeing on keywords in a plugin whose
own rules require parity.

The plugin lints the projects it manages. This lints the plugin.

Usage: selfcheck.py [<plugin-root>]     exit 1 if anything is wrong
"""
import sys, os, io, re, json

ERR, WARN = [], []


def err(m):
    ERR.append(m)


def warn(m):
    WARN.append(m)


def frontmatter(path):
    t = io.open(path, encoding='utf-8').read()
    if not t.startswith('---'):
        return None, t
    end = t.find('\n---', 3)
    if end < 0:
        return None, t
    fm = {}
    for line in t[3:end].split('\n'):
        m = re.match(r'^([a-z-]+):\s*(.*)$', line)
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm, t


def main(root='.'):
    skills_dir = os.path.join(root, 'skills')
    cmds_dir = os.path.join(root, 'commands')
    skills = sorted(d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d)))
    cmds = sorted(f[:-3] for f in os.listdir(cmds_dir) if f.endswith('.md'))

    # 1. every skill directory holds a SKILL.md whose name matches it
    for s in skills:
        p = os.path.join(skills_dir, s, 'SKILL.md')
        if not os.path.exists(p):
            err('skills/%s/ has no SKILL.md — a directory a command can route to and find nothing in' % s)
            continue
        fm, _ = frontmatter(p)
        if not fm:
            err('skills/%s/SKILL.md has no frontmatter' % s)
        elif fm.get('name') != s:
            err('skills/%s/SKILL.md declares name: %s' % (s, fm.get('name')))
        elif not fm.get('description'):
            err('skills/%s/SKILL.md has no description — nothing will ever trigger it' % s)

    # 2. every command declares its tools and points at skills that exist
    for c in cmds:
        p = os.path.join(cmds_dir, c + '.md')
        fm, body = frontmatter(p)
        if not fm:
            err('commands/%s.md has no frontmatter' % c)
            continue
        if not fm.get('description'):
            err('commands/%s.md has no description' % c)
        if not fm.get('allowed-tools'):
            warn('commands/%s.md declares no allowed-tools' % c)
        if '$ARGUMENTS' in body and not fm.get('argument-hint'):
            warn('commands/%s.md uses $ARGUMENTS with no argument-hint' % c)
        for ref in set(re.findall(r'macstack-dev:([a-z-]+)', body)):
            if ref not in skills and ref not in cmds:
                err('commands/%s.md routes to macstack-dev:%s — no such skill or command' % (c, ref))

    # 3. every path a skill names exists
    for s in skills:
        p = os.path.join(skills_dir, s, 'SKILL.md')
        if not os.path.exists(p):
            continue
        body = io.open(p, encoding='utf-8').read()
        for ref in set(re.findall(r'\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./-]+)', body)):
            if not os.path.exists(os.path.join(root, ref)):
                err('skills/%s/SKILL.md points at %s — missing' % (s, ref))
        for ref in set(re.findall(r'`(skills/[A-Za-z0-9_./-]+\.(?:py|json|md))`', body)):
            if not os.path.exists(os.path.join(root, ref)):
                err('skills/%s/SKILL.md points at %s — missing' % (s, ref))

    # 4. every document the contract calls generated HAS a generator
    contract = os.path.join(skills_dir, 'documents', 'references', 'doc-contracts.json')
    if os.path.exists(contract):
        c = json.load(io.open(contract, encoding='utf-8'))
        rend = ''
        rp = os.path.join(skills_dir, 'documents', 'references', 'render.py')
        if os.path.exists(rp):
            rend = io.open(rp, encoding='utf-8').read()
        for key, doc in c.get('documents', {}).items():
            if not doc.get('generated'):
                continue
            base = os.path.basename(doc['path'])
            if base not in rend:
                err('the contract calls %s generated and no generator writes it — '
                    'lint 12.18 is unsatisfiable for that document' % doc['path'])
        # every id space an entity declares must exist
        spaces = set(c.get('id_spaces', {})) | {'slug', 'path', 'filename', 'date-kind'}
        for key, doc in c.get('documents', {}).items():
            for e in doc.get('entities', []):
                if e.get('id_space') not in spaces:
                    err('documents.%s entity %s uses id_space %r, which is not declared'
                        % (key, e.get('kind'), e.get('id_space')))

    # 5. the two manifests agree
    pj = os.path.join(root, '.claude-plugin', 'plugin.json')
    mk = os.path.abspath(os.path.join(root, '..', '..', '.claude-plugin', 'marketplace.json'))
    if os.path.exists(pj) and os.path.exists(mk):
        a = json.load(io.open(pj, encoding='utf-8'))
        entries = json.load(io.open(mk, encoding='utf-8'))
        entries = entries['plugins'] if isinstance(entries, dict) else entries
        b = [e for e in entries if e.get('name') == a.get('name')]
        if not b:
            err('%s is not registered in marketplace.json' % a.get('name'))
        else:
            for f in ('version', 'description', 'keywords'):
                if a.get(f) != b[0].get(f):
                    err('plugin.json and marketplace.json disagree on %s' % f)

    # 6. the README claims what is actually here
    rd = os.path.join(root, 'README.md')
    if os.path.exists(rd):
        t = io.open(rd, encoding='utf-8').read()
        named = set(re.findall(r'`([a-z-]+)`', t))
        missing = [s for s in skills if s not in named]
        if missing:
            warn('README does not mention: %s' % ', '.join(missing))
        claimed = set(re.findall(r'/macstack-dev:([a-z-]+)', t))
        if claimed and claimed != set(cmds):
            err('README commands %s != commands/ %s' % (sorted(claimed), cmds))

    # 7. nothing still names a component that was removed
    dead = ('project-docs', 'render-docs', 'docs-migrate', 'docs-merge', 'plan-changes',
            'sync-spec/SKILL', 'init-project', 'generate-stack', 'discover-context',
            'ROLES.md', 'BUSINESS-LOGIC.md', 'SCREENS.md', 'ROLES-AND-TASKS.md')
    for dirpath, dirnames, names in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ('__pycache__', '.git')]
        for n in names:
            if not n.endswith(('.md', '.json')):
                continue
            p = os.path.join(dirpath, n)
            rel = os.path.relpath(p, root)
            if rel.startswith(('LEARNINGS', 'skills/document-format/references')):
                continue          # history and the migration guide name the old shapes on purpose
            try:
                t = io.open(p, encoding='utf-8').read()
            except Exception:
                continue
            for d in dead:
                if d not in t:
                    continue
                i = t.index(d)
                ctx = t[max(0, i - 500):i + 500].lower()
                # naming an old shape is correct where the text is ABOUT the old shape:
                # a migration step, a "replaces", a note saying what v1 did.
                if any(w in ctx for w in ('migrat', 'replac', 'v1', 'former', 'used to', 'was ')):
                    continue
                warn('%s still names %s' % (rel, d))
                break

    for e in ERR:
        print('ERROR   ' + e)
    for w in WARN:
        print('warning ' + w)
    print('\n%d skills · %d commands · %d errors · %d warnings' % (len(skills), len(cmds), len(ERR), len(WARN)))
    return 1 if ERR else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else '.'))
