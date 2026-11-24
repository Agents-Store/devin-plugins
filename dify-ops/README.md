# dify-ops (Devin plugin)

Dify self-hosted update operations plugin. Pre-flight the target release and the bundled Weaviate migration path, back up volumes with the stack down, merge a release tag into the local dev branch, sync .env variables, and pull and restart containers for Dify Docker deployments.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (4)

- `dify-docker-architecture` — Dify Docker Compose deployment architecture — services, container naming, directory layout, .env.example and envs/ structure, and Docker project name conventions. Use when working with Dify Docker setup, understanding container services, debugging container issues, or needing to know the Dify directory structure. Triggers on "dify docker", "dify containers", "dify services", "dify architecture", "dify compose".

- `env-sync` — Synchronize .env with .env.example for Dify Docker deployments and review the envs/ defaults and override files — new, removed and changed variables, existing values kept, secrets never printed. Use when syncing env variables, checking for new configuration variables, comparing .env.example vs .env, "env sync", "new env variables", "missing environment variables", or after pulling Dify updates. Not for the git merge and backup (update-workflow) or the service layout (dify-docker-architecture).

- `examples` — End-to-end scenario walkthroughs for updating self-hosted Dify. Use when the user asks for "dify update example", "how to update dify", "show me an update walkthrough", "dify upgrade guide", "step-by-step dify update", or needs a complete example of the update process.

- `update-workflow` — Git and backup workflow for updating self-hosted Dify — pick the target tag, pre-flight the bundled Weaviate migration path, back up volumes with the stack down, merge into dev, handle conflicts, pull images, verify, roll back. Use when updating Dify, merging upstream changes, handling merge conflicts in Dify, backing up before an update, or switching to a specific Dify version/tag. Triggers on "update dify", "pull dify changes", "merge main into dev", "upgrade dify", "dify version", "dify backup", "weaviate upgrade".


## Not carried over

- 1 agent(s) — Devin plugins do not support agents
- 2 command(s) — Devin plugins do not support commands

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/dify-ops
