# Notion mapping

How the file-based LLM Wiki concepts map to Notion, plus the exact database definitions and views `init` creates.

## Concept map

| File-based wiki | Notion |
|---|---|
| Vault folder | Root page **LLM Wiki** in a shared teamspace |
| `_schema.md` | **Wiki Schema** page under the root |
| Flat `*.md` articles, `journal/`, `meetings/` | Rows in the **Wiki** database |
| `type/*` tag | `Type` select |
| `status/*` tag | `Status` select |
| `summary:` / `aliases:` / `last-verified:` | `Summary` / `Aliases` / `Last verified` |
| `Topics:` + hub `## Members` Dataview block | `Topics` ↔ `Members` two-way self-relation |
| — (new) who a page is about | `Concerns` ↔ `Concerned in` two-way self-relation to person pages |
| `## Sources` section | `Sources` ↔ `Cited by` relation to the Sources database |
| `_inbox/` / `_sources/` / `_ignore/` | Sources Status `New` / `Ingested` / `Parked` (plus `Ingesting` while claimed) |
| `_log.md` and its append sentinel | Rows in the **Log** database |
| `_Index.md`, `_Timeline.md`, `_Stale.md` | Saved views |
| `[[Wiki Link]]` | Page mention (links by ID; renames never break links) |
| Redlink | Stub page with `Stub` checked |
| Grep for backlinks | `notion-list-page-backlinks` |
| qmd / grep search | `notion-search` with `data_source_url` = Wiki |
| `git log` for the day | Filter on `Last edited` (+ `Last edited by`) |
| Git history | Notion page history (30 days on Plus) and the external backup |
| Callouts `> [!warning]` | Notion callout blocks |
| Dataview / Templater | Dropped; views and relations replace them |

## Database definitions

Create in this order. Each `notion-create-database` call returns a `<data-source>` URL; substitute it for `<…_DS>`.

### 1. Sources

```sql
CREATE TABLE (
  "Name" TITLE,
  "Status" SELECT('New':blue, 'Ingesting':yellow, 'Ingested':green, 'Parked':gray) COMMENT 'Parked = never touch',
  "Kind" SELECT('voice':purple, 'text':default, 'photo':pink, 'link':orange, 'file':brown),
  "Captured" DATE,
  "Captured by" PEOPLE,
  "URL" URL,
  "Files" FILES,
  "Created" CREATED_TIME
)
```

### 2. Wiki

```sql
CREATE TABLE (
  "Name" TITLE,
  "Type" SELECT('topic':blue, 'person':pink, 'org':brown, 'howto':green, 'gotcha':red, 'idea':yellow, 'decision':purple, 'process':orange, 'record':gray, 'meeting':default, 'daily':default, 'planning':default, 'meta':default),
  "Status" SELECT('todo':gray, 'doing':blue, 'waiting':yellow, 'done':green, 'proposed':yellow, 'accepted':green, 'superseded':gray, 'rejected':red),
  "Summary" RICH_TEXT,
  "Aliases" RICH_TEXT COMMENT 'Comma-separated alternate names, incl. German and Russian',
  "Date" DATE COMMENT 'When it happens: daily, planning, meeting, trip, party, appointment',
  "Due" DATE COMMENT 'Next deadline: process next step, record renewal or cancellation',
  "Next step" RICH_TEXT,
  "Owner" PEOPLE COMMENT 'Who drives it (process, record) or whose note it is (daily)',
  "Last verified" DATE,
  "Stub" CHECKBOX,
  "Sources" RELATION('<SOURCES_DS>', DUAL 'Cited by'),
  "Created" CREATED_TIME,
  "Last edited" LAST_EDITED_TIME
)
```

Then, with `notion-update-data-source` on the Wiki data source, add the two self-relations (follow the tool's syntax if it differs; the intent is two-way self-relations with these names):

```sql
ADD COLUMN "Topics" RELATION('<WIKI_DS>', DUAL 'Members' 'members');
ADD COLUMN "Concerns" RELATION('<WIKI_DS>', DUAL 'Concerned in' 'concerned_in')
```

Also try to add a `Last edited by` property (type last edited by). If the tool cannot create it, ask the user to add it in Notion (one click: + property → Last edited by).

### 3. Log

```sql
CREATE TABLE (
  "Name" TITLE,
  "Op" SELECT('init':gray, 'ingest':blue, 'query':green, 'lint':orange, 'daily':default, 'planning':purple, 'schema-update':red, 'backup':brown),
  "Date" DATE,
  "By" PEOPLE,
  "Details" RICH_TEXT,
  "Pages" RELATION('<WIKI_DS>')
)
```

## Views

| Database | View | Setup |
|---|---|---|
| Wiki | **Index** | Table; Type not in daily, planning, meeting, meta; group by Type; sort Name |
| Wiki | **Timeline** | Table; Type in daily, planning, meeting; sort Date descending |
| Wiki | **Processes** | Board; Type = process; group by Status; show Owner, Next step, Due, Concerns |
| Wiki | **Upcoming** | Calendar on Due; Type in process, record; Status not done |
| Wiki | **By person** | Table; Type in process, record; group by Concerns; Status not done |
| Wiki | **Stale** | Table; Last verified before 90 days ago; sort ascending |
| Wiki | **Stubs** | Table; Stub checked; sort Created ascending |
| Wiki | **All pages** | Table; no filter; sort Name. Used by lint with pagination. |
| Sources | **Inbox** | Table; Status in New, Ingesting; sort Captured ascending |
| Log | **Recent** | Table; sort Date descending |
| Log | **Backups** | Table; Op = backup; sort Date descending |

## Limits worth knowing

- Query results cap at 100 rows per call; only view mode paginates.
- SQL mode in `notion-query-data-sources` is quota-limited below Notion Business; rows and view modes are not.
- `notion-search` filters on last-edited date, title-only, and non-relevance sorting need Notion Business; filter on properties in rows mode instead.
- The connector acts as the signed-in person and sees what they can see. Always scope searches to the Wiki data source or the root page.
- Files: up to 5 GB per file on Plus. Connector uploads: `notion-create-file-upload` (local file, up to 20 MiB) or `notion-create-attachment` (inline text or public URL).
