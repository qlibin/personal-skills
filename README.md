# personal-skills

Personal coding-agent skills and agents. Works with any agent tool that reads the open [Agent Skills](https://agentskills.io/specification) format.

## Install

**Claude apps (web, desktop, mobile):** build the zip with `tools/pack.sh <skill>`, then claude.ai → Settings → Capabilities → Skills → Upload. Skills uploaded there also load in Claude Code signed in with the same account, so don't install the same skill through the plugin as well.

**Claude Code only** (skills you never need on mobile):

```
/plugin marketplace add ~/dev/personal-skills
/plugin install personal-skills@personal-skills
```

After a push to GitHub, `/plugin marketplace add <github-user>/personal-skills` works the same way. Run `/plugin marketplace update personal-skills` to pick up changes.

**Other agent tools:**

| Tool | Install |
|---|---|
| Codex | `codex plugin marketplace add <path-or-repo>`, then `codex plugin add personal-skills@personal-skills` |
| Any (Cursor, Gemini, Copilot, ...) | `npx skills add <path-or-repo>` |
| Anything else | symlink `skills/<name>` into the tool's skills folder |

Never copy skill folders by hand: a copy never gets fixes.

## Skills

| Skill | Use when | Install via |
|---|---|---|
| [llm-wiki](skills/llm-wiki/SKILL.md) | building or maintaining an Obsidian (markdown) wiki: ingest, query, lint, daily, weekly | symlink into the Claude config's `skills/` folder (local vaults only) |
| [llm-wiki-notion](skills/llm-wiki-notion/SKILL.md) | a message starts with "wiki": capturing and maintaining the household second brain in Notion. Setup: [references/setup.md](skills/llm-wiki-notion/references/setup.md) | claude.ai upload (needed on mobile) |

## Release

Publish a release in the GitHub UI with a new `v*` tag, or push the tag:

```
git tag v1.0.1 && git push origin v1.0.1
```

Either way, the tag runs the frontmatter check, then attaches `<skill>.zip` for every skill to the GitHub Release, creating the release if needed. Uploading a zip to claude.ai stays a manual step.

## What's here

| Path | Holds |
|---|---|
| `skills/<name>/SKILL.md` | one skill; optional `scripts/` and `references/` beside it |
| `agents/<name>.md` | one subagent |
| `templates/` | starting points for new skills and agents |
| `evals/<skill>-<case>/` | checks that a skill loads when it should and stays out when it shouldn't |
| `tools/check.py` | frontmatter check, run by CI; `--stale` lists artifacts due for review |
| `tools/pack.sh` | builds `dist/<skill>.zip` for claude.ai upload |
| `.claude-plugin/`, `.codex-plugin/`, `.agents/plugins/` | plugin manifests for Claude Code and Codex |
