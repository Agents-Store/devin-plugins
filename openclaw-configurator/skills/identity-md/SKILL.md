---
name: identity-md
description: Guide for creating IDENTITY.md — the agent's name, creature type, vibe, emoji, and avatar in OpenClaw. Use this skill whenever the user is naming their agent, choosing an emoji or avatar, setting up the agent's visual identity, or asking how agent identity works. Even simple questions like "what should I name my agent", "how do I set the bot emoji", or "change the agent's avatar" need this skill.
---

# IDENTITY.md Creation Guide

IDENTITY.md defines the agent's name, nature, vibe, and visual identity. Created during bootstrap, rarely changed after. It's the simplest workspace file.

## Template

```markdown
- Name: (pick something you like)
- Creature: (AI? robot? familiar? ghost in the machine? something weirder?)
- Vibe: (how do you come across? sharp? warm? chaotic? calm?)
- Emoji: (your signature — pick one that feels right)
- Avatar: (workspace-relative path, http(s) URL, or data URI)
```

The docs say: "This isn't just metadata. It's the start of figuring out who you are."

## Field Guidelines

### Name
- Should fit the brand/context (professional for enterprise, playful for personal)
- Must match `@bot_username` if used via Telegram
- Short names work best in chat interfaces (1-2 words)
- Examples: Nova, Atlas, Pixel, Kai, Echo, Onyx

### Creature
- Defines the agent's self-concept
- Options: AI assistant, robot, familiar, digital companion, specialist, advisor
- Domain-specific: "legal advisor", "dev buddy", "creative partner"

### Vibe
- Single-word or short-phrase descriptors
- Examples: sharp, warm, calm, precise, energetic, snarky, professional
- Should align with SOUL.md personality

### Emoji
- Used as message prefix and visual identifier
- Pick something distinctive and relevant
- Common choices by domain:
  - Legal: balance of scales, bookmark, scroll
  - Tech: robot, gear, terminal
  - Creative: sparkles, palette, lightning
  - Personal: star, heart, compass

### Avatar
- Formats accepted:
  - Workspace-relative path: `avatars/agent.png`
  - HTTP/HTTPS URL: `https://example.com/avatar.png`
  - Data URI: `data:image/png;base64,...`
- Keep avatar images in workspace for portability

## Configuration Override

Agent identity can also be set in `openclaw.json` per agent:

```json
{
  "agents": {
    "list": [{
      "id": "main",
      "identity": {
        "name": "Nova",
        "theme": "professional",
        "emoji": "star",
        "avatar": "avatars/nova.png"
      }
    }]
  }
}
```

The `openclaw.json` identity takes precedence over IDENTITY.md for runtime display, but IDENTITY.md remains the agent's self-reference.

## Best Practices

1. Choose a name that's easy to type as a mention (@name)
2. Align vibe with SOUL.md personality
3. Pick one emoji and use it consistently
4. Set the avatar early — it creates visual recognition
5. Rarely needs updating after initial setup
