# Task CLI `v0.0.1`

Minimal CLI for task and project management backed by SQLite.  
**Author:** Jean Carlos Tomicha Ressa · **License:** MIT

---

## Stack

- Python 3 · `argparse` · `sqlite3`
- No external dependencies

## Structure

```
main.py               # CLI entrypoint
projects_manager.sql  # DDL schema
tasks.db              # Database (auto-generated)
```

## Schema

| Table | Description |
|---|---|
| `Project` | Container projects |
| `Task` | Tasks with status, priority, and due date |
| `Tag` | Unique tags (case-insensitive) |
| `TaskTag` | N:M task-tag relation |

**Constraints:** `status ∈ {todo, in_progress, done, cancelled}` · `priority ∈ {1, 2, 3}`  
**FK:** `ON DELETE CASCADE` on `Task → Project` and `TaskTag → Task/Tag`

---

## Usage

### Projects (`p`)

```bash
python main.py p --add --name "name" [--desc "description"]
python main.py p --list
python main.py p --update <id> [--name "x"] [--desc "y"]
python main.py p --delete <id>
```

### Tasks (`t`)

```bash
python main.py t --add --title "name" --pid <project_id>
python main.py t --list [--pid <project_id>]
python main.py t --update <id> [--title "x"] [--status <status>]
python main.py t --delete <id>
```

### Tags (`e`)

```bash
python main.py e --add --name "tag"
python main.py e --list
python main.py e --delete <id>
```

### Link tag to task (`v`)

```bash
python main.py v --add --tid <task_id> --eid <tag_id>
```

---

## Quick Example

```bash
python main.py p --add --name "Backend" --desc "REST API"
python main.py t --add --title "Design endpoints" --pid 1
python main.py e --add --name "urgent"
python main.py v --add --tid 1 --eid 1
python main.py t --update 1 --status in_progress
```

---

## Notes

- DB is auto-created on first run if `projects_manager.sql` exists.
- `PRAGMA foreign_keys = ON` is enforced on every connection.
- Trigger `tr_upd` automatically updates `updated_at` on every `Task` modification.