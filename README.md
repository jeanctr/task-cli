# task-cli `v0.0.1`
Terminal task & project manager. Python + SQLite. Zero dependencies.

## Structure
```
task_cli.py       # CLI entrypoint
task.sql          # DDL schema (auto-applied)
tasks.db          # SQLite database (auto-generated)
```

## Usage
| Cmd | Purpose | Key Flags |
|:---|:---|:---|
| `p` | Projects | `--add --name X`, `--list`, `--update ID`, `--delete ID` |
| `t` | Tasks | `--add --title X --pid ID`, `--list [--pid ID]`, `--update ID --status Y`, `--delete ID` |
| `e` | Tags | `--add --name X`, `--list`, `--delete ID` |
| `v` | Link | `--add --tid T_ID --eid E_ID` |

## Example
```bash
python task_cli.py p --add --name "Backend" --desc "API"
python task_cli.py t --add --title "Auth" --pid 1
python task_cli.py e --add --name "urgent"
python task_cli.py v --add --tid 1 --eid 1
python task_cli.py t --update 1 --status in_progress
```

## Schema & Notes
- **Auto-init:** Creates `tasks.db` from `task.sql` on first run.
- **Task fields:** `status` (enum), `priority` (1-3), `due_date`, `parent_id` (subtasks), `description`.
- **Integrity:** `PRAGMA foreign_keys = ON` · `CHECK` constraints · `ON DELETE CASCADE/SET NULL`.
- **Performance:** Composite `(project_id, status)` & partial `(due_date)` indexes · `TaskTag` uses `WITHOUT ROWID`.
- **Audit:** `updated_at` auto-managed by DB trigger. CLI stays stateless.