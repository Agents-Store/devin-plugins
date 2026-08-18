---
name: bootstrap-boot
description: Guide for BOOTSTRAP.md (first-run setup ritual) and BOOT.md (gateway restart checklist) in OpenClaw. Use this skill whenever the user is setting up a new agent for the first time, configuring onboarding flows, creating first-run discovery processes, or defining what should happen on gateway restart. Even questions like "what should happen when the agent starts for the first time", "how do I initialize a fresh agent", or "what runs on reboot" need this skill.
---

# BOOTSTRAP.md and BOOT.md Guide

Two special-purpose files that run at specific lifecycle events.

## BOOTSTRAP.md — First-Run Ritual

### Purpose
One-time setup instructions for a fresh agent. The agent follows these on first session, then **deletes the file** — it should never run twice.

### When It Runs
- Created during `openclaw setup` or `openclaw onboard` for brand-new workspaces
- Only when BOOTSTRAP.md exists in the workspace
- Triggered on the very first session after workspace creation
- After completion, the agent deletes BOOTSTRAP.md

### Official Template Concept

The template establishes a conversational discovery process:

> "You just woke up. Time to figure out who you are."

**Discovery flow:**
1. Ask who you are and who they are (organic conversation, not interrogation)
2. Discover four elements:
   - **Name** — what they should call you
   - **Creature** — what type of entity you are
   - **Vibe** — communication style
   - **Emoji** — personal signature
3. Document: update IDENTITY.md and USER.md
4. Collaborate on SOUL.md — what matters to them, behavioral preferences
5. Optionally set up channels (web chat, WhatsApp, Telegram)
6. Delete BOOTSTRAP.md — you're no longer a fresh instance

### Custom BOOTSTRAP.md Example

For a pre-configured agent (not interactive discovery):

```markdown
# BOOTSTRAP.md — First Run Setup

You're being set up for [Company Name] as a [role].

## Step 1: Verify Identity
Read IDENTITY.md — confirm your name and emoji are set.

## Step 2: Verify User Profiles
Read USER.md — confirm all team members are listed.

## Step 3: Verify Configuration
Read AGENTS.md and SOUL.md — confirm they match the intended setup.

## Step 4: Test Channels
Send a test message via each configured channel:
- Telegram: send "Hello, I'm online!" to the primary user
- Discord: post in the designated channel

## Step 5: Read Documentation
Read all files in docs/ to build initial context.

## Step 6: Confirm Setup
Report setup status to the primary user.

## Step 7: Clean Up
Delete this file (BOOTSTRAP.md) — setup is complete.
```

### Key Rules for BOOTSTRAP.md
1. Always end with "delete this file"
2. Keep instructions concrete and sequential
3. Can be conversational (discovery) or procedural (pre-configured)
4. Maximum 20,000 characters (bootstrapMaxChars limit)
5. BOOTSTRAP.md is auto-injected into context while present — it counts toward char limits
6. Can be skipped: start with `--dev` flag, or set `agent.skipBootstrap: true` in openclaw.json

---

## BOOT.md — Gateway Restart Checklist

### Purpose
Instructions executed when the OpenClaw gateway restarts. Unlike BOOTSTRAP.md, BOOT.md is NOT deleted — it runs on every restart.

### When It Runs
- On gateway restart (when `hooks.internal.enabled` is set)
- NOT on every session — only on gateway process restart
- The agent reads BOOT.md and follows the instructions

### Official Template

```markdown
# BOOT.md
# Add short, explicit instructions for what OpenClaw should do on startup.
# Requires: hooks.internal.enabled in openclaw.json
```

### When Messages Arrive During Boot
If a task sends a message during boot, use the message tool then reply with `NO_REPLY`.

### Custom BOOT.md Example

```markdown
# BOOT.md — Gateway Restart Checklist

## On Restart
1. Check system status (uptime, connected channels)
2. Read today's memory file for context continuity
3. Verify all configured channels are connected
4. Check for pending standing orders that were missed during downtime
5. Send status report to primary user if downtime > 5 minutes
```

### Key Rules for BOOT.md
1. Keep very short — runs on every restart
2. Focus on system recovery, not regular tasks
3. Don't duplicate HEARTBEAT.md content
4. Requires `hooks.internal.enabled` in openclaw.json

## Best Practices

1. **BOOTSTRAP.md**: use for one-time setup of new agents. Either interactive discovery or pre-configured checklist.
2. **BOOT.md**: use only if you need specific actions on gateway restart. Most agents can skip this file entirely.
3. Both files should be lean — they have the same 20K character limit as other bootstrap files.
4. Test BOOTSTRAP.md on a fresh workspace before deploying to production.
