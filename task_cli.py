"""
Task CLI v0.0.1
Minimal terminal task & project manager backed by SQLite.
Zero external dependencies · Author: Jean Carlos Tomicha Ressa · License: MIT
"""
import argparse
import os
import sqlite3

DB, SQL = 'tasks.db', 'task.sql'


def get_db():
    """Return a configured SQLite connection.
    Auto-creates DB from `task.sql` if missing. Enables FKs & dict-like row access."""
    c = sqlite3.connect(DB)
    c.execute("PRAGMA foreign_keys = ON;")
    c.row_factory = sqlite3.Row  # Rows behave like dicts: row['col_name']
    if not os.path.exists(DB) and os.path.exists(SQL):
        with open(SQL, 'r') as f:
            c.executescript(f.read())  # Run DDL only once
    return c


# --- PROJECTS ---

def add_proj(name, desc):
    """Insert a new project. Returns & prints the generated ID."""
    with get_db() as c:
        pid = c.execute("INSERT INTO Project (name, description) VALUES (?, ?)", (name, desc)).lastrowid
        print(f"SUCCESS: Project '{name}' (ID: {pid})")


def list_projs():
    """Fetch & print all projects."""
    with get_db() as c:
        rows = c.execute("SELECT * FROM Project").fetchall()
    if not rows:
        return print("INFO: No projects.")
    for r in rows:
        print(f"[{r['id']}] {r['name']} | {r['description'] or 'N/A'}")


def upd_proj(pid, name=None, desc=None):
    """Update project name/description. Safe dynamic query (columns are hardcoded)."""
    if not name and not desc:
        return print("ERR: Need --name or --desc")
    cols, vals = [], []
    if name:
        cols.append("name=?")
        vals.append(name)
    if desc:
        cols.append("description=?")
        vals.append(desc)
    with get_db() as c:
        c.execute(f"UPDATE Project SET {','.join(cols)} WHERE id=?", (*vals, pid))
        print(f"SUCCESS: Project {pid} updated")


def del_proj(pid):
    """Delete project & cascade to its tasks."""
    with get_db() as c:
        c.execute("DELETE FROM Project WHERE id=?", (pid,))
        print(f"SUCCESS: Project {pid} deleted")


# --- TASKS ---

def add_task(title, project_id):
    """Insert a task. Validates project_id via FK constraint."""
    try:
        with get_db() as c:
            tid = c.execute("INSERT INTO Task (title, project_id) VALUES (?, ?)", (title, project_id)).lastrowid
            print(f"SUCCESS: Task '{title}' (ID: {tid})")
    except sqlite3.IntegrityError:
        print("ERR: Bad Project ID")


def list_tasks(project_id=None):
    """List all tasks, optionally filtered by project."""
    query, params = "SELECT * FROM Task", ()
    if project_id:
        query += " WHERE project_id=?"
        params = (project_id,)
    with get_db() as c:
        rows = c.execute(query, params).fetchall()
    if not rows:
        return print("INFO: No tasks.")
    for r in rows:
        print(f"[{r['id']}] [{r['status'].upper()}] {r['title']} (Proj: {r['project_id']})")


def upd_task(tid, title=None, status=None):
    """Update task title/status. Validates status against allowed enum."""
    if not title and not status:
        return print("ERR: Need --title or --status")
    cols, vals = [], []
    if title:
        cols.append("title=?")
        vals.append(title)
    if status:
        if status not in ('todo', 'in_progress', 'done', 'cancelled'):
            return print("ERR: Bad status")
        cols.append("status=?")
        vals.append(status)
    with get_db() as c:
        c.execute(f"UPDATE Task SET {','.join(cols)} WHERE id=?", (*vals, tid))
        print(f"SUCCESS: Task {tid} updated")


def del_task(tid):
    """Delete task. Cascades to TaskTag junction table."""
    with get_db() as c:
        c.execute("DELETE FROM Task WHERE id=?", (tid,))
        print(f"SUCCESS: Task {tid} deleted")


# --- TAGS ---

def add_tag(name):
    """Insert a tag. Fails gracefully if UNIQUE constraint triggers."""
    try:
        with get_db() as c:
            eid = c.execute("INSERT INTO Tag (name) VALUES (?)", (name,)).lastrowid
            print(f"SUCCESS: Tag '{name}' (ID: {eid})")
    except sqlite3.IntegrityError:
        print("ERR: Tag exists")


def list_tags():
    """Fetch & print all tags."""
    with get_db() as c:
        rows = c.execute("SELECT * FROM Tag").fetchall()
    if not rows:
        return print("INFO: No tags.")
    for r in rows:
        print(f"[{r['id']}] {r['name']}")


def del_tag(eid):
    """Delete tag. Cascades from TaskTag."""
    with get_db() as c:
        c.execute("DELETE FROM Tag WHERE id=?", (eid,))
        print(f"SUCCESS: Tag {eid} deleted")


# --- LINK ---

def link(task_id, tag_id):
    """Associate a task with a tag. Fails if IDs are invalid or link exists."""
    try:
        with get_db() as c:
            c.execute("INSERT INTO TaskTag (task_id, tag_id) VALUES (?, ?)", (task_id, tag_id))
            print(f"SUCCESS: Tag {tag_id} linked to Task {task_id}")
    except sqlite3.IntegrityError:
        print("ERR: Bad Link")


# --- CLI ---

def cli():
    """Parse arguments & route to CRUD functions.
    Uses mutually exclusive groups to enforce single action per call."""
    p = argparse.ArgumentParser(description="Minimal SQLite Task Manager")
    s = p.add_subparsers(dest="cmd")

    # Projects
    ps = s.add_parser("p")
    g = ps.add_mutually_exclusive_group(required=True)
    g.add_argument("--add", action="store_true")
    g.add_argument("--list", action="store_true")
    g.add_argument("--update", type=int, metavar="ID")
    g.add_argument("--delete", type=int, metavar="ID")
    ps.add_argument("--name")
    ps.add_argument("--desc")

    # Tasks
    ts = s.add_parser("t")
    g = ts.add_mutually_exclusive_group(required=True)
    g.add_argument("--add", action="store_true")
    g.add_argument("--list", action="store_true")
    g.add_argument("--update", type=int, metavar="ID")
    g.add_argument("--delete", type=int, metavar="ID")
    ts.add_argument("--title")
    ts.add_argument("--pid", type=int)
    ts.add_argument("--status")

    # Tags (named 'e' to avoid conflict with 't')
    es = s.add_parser("e")
    g = es.add_mutually_exclusive_group(required=True)
    g.add_argument("--add", action="store_true")
    g.add_argument("--list", action="store_true")
    g.add_argument("--delete", type=int, metavar="ID")
    es.add_argument("--name")

    # Link (Task <-> Tag)
    vs = s.add_parser("v")
    vs.add_argument("--add", action="store_true", required=True)
    vs.add_argument("--tid", type=int)
    vs.add_argument("--eid", type=int)

    args = p.parse_args()
    if not args.cmd:
        return p.print_help()

    # --- ROUTING ---
    # Note: `is not None` is used for --update/--delete because `0` is a valid ID.
    if args.cmd == "p":
        if args.add:
            add_proj(args.name, args.desc) if args.name else print("ERR: --name")
        elif args.list:
            list_projs()
        elif args.update is not None:
            upd_proj(args.update, args.name, args.desc)
        elif args.delete is not None:
            del_proj(args.delete)

    elif args.cmd == "t":
        if args.add:
            add_task(args.title, args.pid) if args.title and args.pid else print("ERR: --title, --pid")
        elif args.list:
            list_tasks(args.pid)
        elif args.update is not None:
            upd_task(args.update, args.title, args.status)
        elif args.delete is not None:
            del_task(args.delete)

    elif args.cmd == "e":
        if args.add:
            add_tag(args.name) if args.name else print("ERR: --name")
        elif args.list:
            list_tags()
        elif args.delete is not None:
            del_tag(args.delete)

    elif args.cmd == "v":
        if args.add:
            link(args.tid, args.eid) if args.tid and args.eid else print("ERR: --tid, --eid")


if __name__ == '__main__':
    cli()