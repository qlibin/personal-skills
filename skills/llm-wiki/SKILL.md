---
name: llm-wiki
description: >
  Build and maintain an interconnected Obsidian knowledge base (wiki) from source documents.
  Supports ingest (compile sources into wiki articles), query (answer questions and file results
  back into the wiki), lint (health-check the wiki for issues), and daily / weekly (write the
  journal notes from the day's or week's captures and activity).
  Follows Karpathy's LLM Wiki method — the wiki is a persistent, compounding artifact
  maintained entirely by the LLM.
metadata:
  owner: qlibin
  last-verified: "2026-11-07"
---

# Obsidian Knowledge Base — LLM Wiki

Build and maintain an interconnected Obsidian wiki following Karpathy's LLM Wiki method. The wiki is a persistent, compounding artifact — the LLM writes and maintains all of it. The user curates sources, directs analysis, and asks questions. The LLM does the summarizing, cross-referencing, filing, and bookkeeping.

## Invocation

```
/llm-wiki <operation> [args...]
```

### Operations

| Operation | Syntax | Description |
|-----------|--------|-------------|
| **ingest** | `/llm-wiki ingest <source-path> [vault-path]` | Read sources and compile into wiki articles |
| **query** | `/llm-wiki query <vault-path> "<question>"` | Answer a question from the wiki, optionally filing the result as a new page |
| **lint** | `/llm-wiki lint <vault-path>` | Health-check the wiki for issues |
| **init** | `/llm-wiki init <vault-path>` | Initialize a new empty vault with schema and structure |
| **daily** | `/llm-wiki daily [date] [vault-path]` | Write the daily journal note from the `_inbox/` capture and the day's touched pages |
| **weekly** | `/llm-wiki weekly [YYYY-Www] [vault-path]` | Roll the week's dailies and activity into the weekly note |

If no operation is given, default to **ingest**.

- `<source-path>` — directory containing source documents (or a single file). Supports: `.md`, `.txt`, `.pdf`, `.json`, `.html`, `.csv`, `.yaml`, `.yml`, `.xml`, `.log`, `.py`, `.scala`, `.ts`, `.js`, `.go`, `.java`, `.sh`, `.sql`, and other text formats.
- `[vault-path]` — output directory for the Obsidian vault. Defaults to `./obsidian-vault/` in the current working directory.

**Arguments:** `$ARGUMENTS`

---

## Architecture

The wiki has three layers:

**Raw sources** (`_sources/`) — the user's curated collection of source documents. Articles, papers, code, data files. These are immutable — the LLM reads from them but never modifies them. This is the source of truth.

**The wiki** (root of vault) — LLM-generated markdown files. Summaries, entity pages, concept pages, comparisons, an overview, a synthesis. The LLM owns this layer entirely. It creates pages, updates them when new sources arrive, maintains cross-references, and keeps everything consistent.

**The schema** (`_schema.md`) — a document that tells the LLM how the wiki is structured, what the conventions are, and what workflows to follow. The user and LLM co-evolve this over time. On first compilation, the LLM generates a sensible default schema based on the domain. On subsequent runs, the LLM reads and follows the existing schema.

---

## Operation: init

Initialize an empty vault with the directory structure and schema.

1. Create the vault directory.
2. Create `_sources/` subdirectory.
3. Generate `_schema.md` with default conventions (or ask the user about their domain to customize).
4. Create empty `_Index.md` and `_log.md`.
5. Print the vault path and instructions.

---

## Operation: ingest

You MUST follow these phases in order. Use the TaskCreate tool to track progress through each phase.

### Phase 1: Read Schema & Existing State

1. If the vault already exists, read `_schema.md` to understand conventions.
2. Read `_Sources.md` (if it exists) to know what's already been ingested.
3. Read `_Index.md` to understand existing article structure.
4. Identify NEW source documents not yet in the registry.

If the vault does not exist, run `init` first.

### Phase 2: Scan & Ingest Sources

1. **Scan** the source path recursively. List every file with its path, size, and type.
2. **Read** each source document. For very large files (>2000 lines), read in chunks and summarize.
3. **Create a source manifest** — a structured list of all documents with:
   - Relative path from source root
   - Document type (article, paper, code, config, data, notes, etc.)
   - A 1-2 sentence summary of content
   - Key topics/entities mentioned

### Phase 3: Concept Extraction & Taxonomy

From the source manifest, identify:

1. **Core concepts** — the main ideas, technologies, patterns, entities, or topics across all documents. Each concept becomes an article.
2. **Relationships** — how concepts relate to each other (e.g., "implements", "depends on", "is a type of", "contrasts with").
3. **Categories** — group concepts into 3-7 top-level categories for organization.
4. **Hierarchy** — identify which concepts are broad (overview articles) vs. narrow (detail articles).

**Aim for 1 article per distinct concept.** Don't create an article for every source document — synthesize across sources. A single concept article may draw from multiple source documents. A single dense source may spawn multiple concept articles.

**Naming convention:** Use clear, descriptive names in Title Case. Examples: `Entitlement Selection Logic.md`, `DynamoDB Schema Versioning.md`.

### Phase 4: Generate Articles

For each concept, generate a markdown article following this template:

```markdown
---
tags:
  - <category-tag>
  - <additional-tags>
sources:
  - "[[_sources/<source-filename>]]"
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
---

# <Concept Title>

<Opening paragraph: concise definition/summary — 2-4 sentences.>

## Overview

<Expanded explanation. Use wiki-links like [[Other Concept]] whenever referencing
another concept that has its own article. Be generous with links on first mention.>

## <Relevant Section Headings>

<Organize the body by whatever structure fits the concept:
  - For a technology: How It Works, Configuration, Gotchas
  - For a process: Steps, Inputs/Outputs, Error Handling
  - For an entity: Attributes, Relationships, Lifecycle
  - For a pattern: Problem, Solution, Trade-offs, Examples>

## Key Details

<Bullet points of important specifics, numbers, thresholds, edge cases.>

## Related

- [[Related Concept 1]] — <one-line description of relationship>
- [[Related Concept 2]] — <one-line description of relationship>
```

**Article writing rules:**

- **Wiki-links are mandatory.** Every reference to another concept MUST use `[[Concept Name]]` syntax. This is what makes the Obsidian graph view useful.
- **Backlinks must be bidirectional.** If A links to B, B should link back to A (in its body or Related section).
- **Synthesize, don't copy.** Rewrite information in clear prose. Quote sparingly and only for important exact wording.
- **Be specific.** Include concrete details: numbers, thresholds, config values, code snippets, command examples.
- **Flag contradictions.** If new data contradicts existing claims, note the contradiction explicitly. Don't silently overwrite — the user needs to see the conflict.
- **Use Obsidian features:**
  - `> [!note]` / `> [!warning]` / `> [!tip]` callouts for important asides
  - `> [!example]` for examples
  - Code blocks with language tags for code/config snippets
  - Mermaid diagrams (` ```mermaid `) for flows and relationships where helpful
  - `#tags` in frontmatter for categorization
  - YAML frontmatter with tags, sources, dates for Dataview compatibility
- **Keep articles focused.** One concept per article. If an article exceeds ~500 lines, split it.

### Phase 5: Build Index & Navigation

Create or update these special files in the vault root:

#### `_Index.md` (Map of Content)

Content-oriented catalog of everything in the wiki. Each page listed with a link, a one-line summary, and organized by category. The LLM reads this first when answering queries to find relevant pages.

```markdown
---
tags:
  - meta
  - index
updated: <date>
---

# <Knowledge Base Title>

> Compiled knowledge base: <N> sources, <M> articles.
> Last updated: <date>

## Categories

### <Category 1>
- [[Article 1]] — <one-line summary>
- [[Article 2]] — <one-line summary>

### <Category 2>
- [[Article 3]] — <one-line summary>
...

## Quick Reference

<Brief paragraph or table summarizing the most important takeaways across the entire knowledge base.>

## Source Documents

See [[_Sources]] for the complete list of ingested source documents.
```

#### `_Sources.md` (Source Document Registry)

```markdown
---
tags:
  - meta
  - sources
updated: <date>
---

# Source Documents

| # | Source | Type | Summary | Articles |
|---|--------|------|---------|----------|
| 1 | `filename.md` | article | Brief summary | [[Art1]], [[Art2]] |
| 2 | `data.json` | data | Brief summary | [[Art3]] |
...
```

#### `_log.md` (Chronological Activity Log)

Append-only record of what happened and when. Each entry uses a consistent prefix for parseability (`grep "^## \[" _log.md | tail -5` gives the last 5 entries).

```markdown
---
tags:
  - meta
  - log
---

# Activity Log

## [2026-04-10] ingest | Source Document Title
- Ingested 3 new source documents
- Created articles: [[Article A]], [[Article B]]
- Updated articles: [[Article C]] (added new section on X)

## [2026-04-10] query | "What is the relationship between X and Y?"
- Filed result as [[X vs Y Comparison]]

## [2026-04-11] lint | Health check
- Fixed 2 broken links
- Added backlinks to 3 articles
- Created stub for [[Missing Concept]]
```

### Phase 6: Source Archival

Create a `_sources/` subdirectory in the vault. For each source document:

- If it's already markdown: copy it into `_sources/` with a frontmatter header noting it's a source document.
- If it's another text format: copy it into `_sources/` as-is or convert to markdown.
- If it's too large or binary: create a stub in `_sources/` with metadata pointing to the original path.

### Phase 7: Schema Generation/Update

If `_schema.md` doesn't exist, create it documenting:
- The categories and taxonomy used
- Naming conventions
- Article structure conventions
- Any domain-specific rules discovered during compilation

If it already exists, update it with any new categories or conventions.

### Phase 8: Validation & Lint

Run the lint operation (see below) and fix any issues found.

### Phase 9: Log & Summary

1. Append an entry to `_log.md` recording what was ingested.
2. Print a summary:

```
Obsidian vault updated successfully!

  Vault:      <vault-path>
  Sources:    <N> documents ingested (<new> new, <existing> existing)
  Articles:   <M> concept articles (<created> created, <updated> updated)
  Links:      <L> wiki-links
  Categories: <list>

  Open in Obsidian: vault path above
  Entry point: _Index.md
```

---

## Operation: daily

Write the daily journal note for one day. Default date: today. Default vault: the current working directory if it holds `_schema.md`, else `./obsidian-vault/`.

The note is a **thin index of the day**, not a place facts live. Everything durable belongs on its own page; the daily links to it.

1. **Read the schema** (`_schema.md`) and the daily template (`_templates/daily.md`). The schema's writing rules and layout win over anything here.
2. **Read the capture.** `_inbox/<date>.md` if it exists — the user's own rough draft of the day. Never read `_ignore/`.
3. **Find the day's activity** without guessing:
   - `git log --since=<date> --until=<date+1day> --name-only` for pages touched and committed.
   - `git status --short` for uncommitted work.
   - `git diff` on modified pages to see what actually changed, rather than inferring from the filename.
4. **Read the previous daily note** and carry over any unfinished `## Follow-ups`. Drop the ones the day closed.
5. **Write `journal/daily/YYYY-MM-DD.md`** from the template. Rules:
   - **One line per item, with a link to the page that owns it.** If a bullet needs a second sentence, that sentence belongs on the owner page.
   - **No jargon and no internal shorthand.** Write it so a reader outside the team understands the sentence. Ticket IDs and system names are fine; unexplained mechanism is not.
   - **Do not restate what a durable page owns.** The bullet says what happened and where to read it. Counts, tables, stack traces, and reasoning stay on the owner page.
   - `## Learned` holds only things that are true beyond today, each linking to the page that now holds it. If nothing durable was learned, leave it empty.
   - `## Follow-ups` are actionable and link to the owner page.
   - Preserve the Dataview block verbatim, with the date substituted.
   - Frontmatter: `type/daily`, and `Topics:` for the day's themes as quoted wiki-links.
6. **Consume the capture.** Delete `_inbox/<date>.md` — a daily draft is not archived to `_sources/`; the note replaces it. Leave any other `_inbox/` file alone; it is ingest's queue, not this operation's.
7. **Append to `_log.md`** as `[<date>] ingest | Daily note for <date>`, inserted at the **last** occurrence of the append sentinel.

If the day produced durable facts that no page owns yet, say so and offer to write those pages — do not smuggle them into the daily.

---

## Operation: weekly

Roll one ISO week into `journal/weekly/YYYY-Www.md`. Default week: the one containing today. Same vault defaults as `daily`.

The weekly is **not a concatenation of the dailies**. It is what the week amounted to, at one level up.

1. **Read the schema** and `_templates/weekly.md`.
2. **Read every daily in the week** (`journal/daily/`, including month buckets) and the previous weekly note.
3. **Read the week's activity**: `git log --since=<monday> --until=<sunday+1day>` for what landed, plus any `meetings/` notes dated in the week.
4. **Write the note**, following the template's sections. Rules:
   - **Say what the week amounted to, not what each day contained.** If a thread ran over several days, it is one line naming the outcome, not five lines of progress.
   - **Never repeat a daily verbatim.** A line that only restates one day's bullet should be cut or merged into the thread it belongs to.
   - One line per item, each linking to the page that owns it. Link dailies by basename (`[[YYYY-MM-DD]]`), never by path.
   - No jargon; plain language, readable by a non-native speaker.
   - `## Shipped` is what actually landed — merged, deployed, decided, accepted. Not what was worked on.
   - `## Learned` holds only what outlived the week, each linking to its durable page.
   - `## Next week` carries the open follow-ups from the dailies, deduplicated.
   - Preserve the Dataview block verbatim.
5. **Append to `_log.md`** as `[<date>] ingest | Weekly note for <YYYY-Www>`, at the last sentinel occurrence.

If a week has gaps (missing dailies), note them in the summary rather than inventing what happened.

---

## Operation: query

Answer a question using the wiki as the knowledge base.

1. Read `_Index.md` to find relevant pages.
2. Read relevant wiki articles (not raw sources — the wiki is the compiled knowledge).
3. Synthesize an answer with `[[wiki-links]]` citations.
4. **Ask the user if the answer should be filed as a new wiki page.** Good answers — comparisons, analyses, connections — are valuable and shouldn't disappear into chat history. If filed:
   - Write it as a standard article with frontmatter, tags, and wiki-links.
   - Update `_Index.md` to include the new page.
   - Append to `_log.md`.
5. If the answer reveals gaps in the wiki (concepts mentioned but lacking pages, outdated information), note them and offer to create/update pages.

---

## Operation: lint

Health-check the wiki. Scan all files and report on:

1. **Broken links** — `[[...]]` wiki-links pointing to non-existent files. Fix them.
2. **Orphan pages** — articles with no inbound links. Add links from relevant articles or the index.
3. **Missing backlinks** — if A links to B but B doesn't link to A, add the backlink.
4. **Contradictions** — flag where newer sources have superseded older claims across articles.
5. **Stale content** — articles that haven't been updated despite newer sources being available.
6. **Missing concepts** — important concepts mentioned in articles but lacking their own page. Offer to create stubs or full articles.
7. **Missing cross-references** — places where two articles discuss related topics but don't link to each other.
8. **Tag consistency** — verify all articles have frontmatter tags using a consistent vocabulary.
9. **Index completeness** — verify every article appears in `_Index.md`.
10. **Data gaps** — suggest new questions to investigate or new sources to look for.

After reporting, offer to fix the issues found. Append a lint entry to `_log.md`.

---

## Incremental Updates

When the vault already exists:

1. **Never delete existing articles** unless explicitly asked. Always ADD to the knowledge base.
2. When updating an existing article with new information, update its `updated:` frontmatter date.
3. When new data contradicts existing claims, flag the contradiction visibly — don't silently overwrite.
4. The wiki should keep getting richer with every source added and every question asked.

---

## Important Notes

- The user does NOT manually edit the wiki — the LLM maintains it entirely.
- Prefer QUALITY over QUANTITY. 20 well-linked, substantive articles beat 50 shallow stubs.
- The Obsidian graph view is a key feature. Dense, meaningful interlinking is what makes it valuable.
- Use relative links and standard Obsidian syntax. No HTML unless absolutely necessary.
- Respect the source material's accuracy. Don't hallucinate facts not present in the sources.
- If a source is ambiguous or contradictory, note the ambiguity explicitly in the article.
- Good answers to queries should be filed back into the wiki — explorations compound just like ingested sources.
- The wiki is just a directory of markdown files. It can be version-controlled with git.
