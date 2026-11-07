# Working in personal-skills

Rules for adding or changing a skill or agent.

## Adding an artifact

1. Copy `templates/skill.md` to `skills/<name>/SKILL.md`, or `templates/agent.md` to `agents/<name>.md`.
2. `name` must match the folder or file name: lowercase, digits and hyphens, max 64 characters.
3. `description` says what it does and when to use it ("Use when ..."), trigger words first, in as few words as will trigger it. Every installed skill's description is loaded into every session.
4. Set `metadata.owner` and `metadata.last-verified` (YYYY-MM-DD).
5. Add two eval cases (copy `evals/llm-wiki-notion-*`): one request that should load the skill, one nearby request that should not.
6. Run `python3 tools/check.py`, then `claude plugin eval . --case '<name>-*' --runs 3 --ablation none`.
7. Add the skill to the table in `README.md`, with how it is installed.

## Rules

- **Link to the source of truth; don't copy it.**
- **No secrets, endpoints or IDs written in.** Discover them at runtime or read them from a per-user env file.
- **Name by capability**, so a skill outlives the project that prompted it.
- **Standard frontmatter only** in `SKILL.md`: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. `tools/check.py` rejects anything else.
- **Scripts go in the skill's `scripts/` folder** and get reviewed like code: they run with your own access.
- **One install path per skill.** A skill uploaded to claude.ai syncs into Claude Code; installing it through the plugin as well loads it twice.

## Keeping it alive

- Bump `metadata.last-verified` when you use or change an artifact.
- Re-run a skill's evals when its `description` changes or after a major model release.
- Every quarter, run `python3 tools/check.py --stale`; renew or delete what it lists.
