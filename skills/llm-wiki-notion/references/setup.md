# Setup

For each person in the household. The wiki Owner does step 4 once; everyone else skips it.

## What you need

- A Notion account that is a **member** of the household workspace (Plus plan). Guests cannot use the Claude connector.
- A Claude account (Free works; Pro if you use it a lot).

## Steps

1. **Connect Notion.** In Claude (web or desktop): Settings → Connectors → Notion → Connect. Sign in with your own Notion account and pick the household workspace.
2. **Turn on code execution.** Settings → Capabilities → Code execution and file creation: on. Skills need it.
3. **Install the skill.** Settings → Capabilities → Skills → Upload skill → choose `llm-wiki-notion.zip`. It then works in the Claude apps and in Claude Code signed in with the same account.
4. **Owner only, once:** in Claude Code or desktop, say `wiki init`. Then share the teamspace with the other members.
5. **Add the fallback line** to Settings → Profile → "What personal preferences should Claude consider". It keeps capture working where skills do not load (for example hands-free voice mode):

   > When I say "wiki capture: …", create a row in the Notion database "Sources" under "LLM Wiki" with Status "New", Captured = today, Captured by = me, and my exact words as the body. Do nothing else.

6. **Test.** On your phone: `wiki capture: test note`. Check that a row appears in Sources → Inbox.

## Everyday use

| Say | What happens |
|---|---|
| `wiki capture: …` | Saves your words as they are. Fast. |
| `wiki capture and ingest: …` | Saves and files it into the wiki right away |
| `wiki ingest` | Files all new captures into wiki pages and processes |
| `wiki, what do we know about …` | Answers from the wiki |
| `wiki daily` | Writes your daily note |
| `wiki planning prep` / `wiki planning close: …` | Before and after the planning session together |
| `wiki lint` | Health check, incl. overdue deadlines and backup age |

## Updating the skill

When the Owner sends a new `llm-wiki-notion.zip`: Settings → Capabilities → Skills → remove the old one → upload the new one.
