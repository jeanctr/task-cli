"""
Task CLI v0.0.1
Author: Jean Carlos Tomicha Ressa | License: MIT
"""
import argparse
import os
import sqlite3

DB, SQL = 'tasks.db', 'projects_manager.sql'


def get_db():
    c = sqlite3.connect(DB)
    c.execute("PRAGMA foreign_keys = ON;")
    c.row_factory = sqlite3.Row
    if not os.path.exists(DB) and os.path.exists(SQL):
        with open(SQL, 'r') as f:
            c.executescript(f.read())
    return c

# --- PROJECTS ---


def add_proj(n, d):
    with get_db() as c:
        id = c.execute(
            "INSERT INTO Project (name, description) VALUES (?, ?)", (n, d)).lastrowid
        print(f"SUCCESS: Project '{n}' (ID: {id})")


def list_projs():
    with get_db() as c:
        rows = c.execute("SELECT * FROM Project").fetchall()
    if not rows:
        return print("INFO: No projects.")
    for r in rows:
        print(f"[{r['id']}] {r['name']} | {r['description'] or 'N/A'}")


def upd_proj(id, n=None, d=None):
    if not n and not d:
        return print("ERR: Need --name or --desc")
    q, v = [], []
    if n:
        q.append("name=?")
        v.append(n)
    if d:
        q.append("description=?")
        v.append(d)
    with get_db() as c:
        c.execute(f"UPDATE Project SET {','.join(q)} WHERE id=?", (*v, id))
        print(f"SUCCESS: Project {id} updated")


def del_proj(id):
    with get_db() as c:
        c.execute("DELETE FROM Project WHERE id=?", (id,))
        print(f"SUCCESS: Project {id} deleted")

# --- TASKS ---


def add_task(t, pid):
    try:
        with get_db() as c:
            id = c.execute(
                "INSERT INTO Task (title, project_id) VALUES (?, ?)", (t, pid)).lastrowid
            print(f"SUCCESS: Task '{t}' (ID: {id})")
    except sqlite3.IntegrityError:
        print("ERR: Bad Project ID")


def list_tasks(pid=None):
    q, v = "SELECT * FROM Task", ()
    if pid:
        q += " WHERE project_id=?"
        v = (pid,)
    with get_db() as c:
        rows = c.execute(q, v).fetchall()
    if not rows:
        return print("INFO: No tasks.")
    for r in rows:
        print(
            f"[{r['id']}] [{r['status'].upper()}] {r['title']} (Proj: {r['project_id']})")


def upd_task(id, t=None, s=None):
    if not t and not s:
        return print("ERR: Need --title or --status")
    q, v = [], []
    if t:
        q.append("title=?")
        v.append(t)
    if s:
        if s not in ('todo', 'in_progress', 'done', 'cancelled'):
            return print("ERR: Bad status")
        q.append("status=?")
        v.append(s)
    with get_db() as c:
        c.execute(f"UPDATE Task SET {','.join(q)} WHERE id=?", (*v, id))
        print(f"SUCCESS: Task {id} updated")


def del_task(id):
    with get_db() as c:
        c.execute("DELETE FROM Task WHERE id=?", (id,))
        print(f"SUCCESS: Task {id} deleted")

# --- TAGS ---


def add_tag(n):
    try:
        with get_db() as c:
            id = c.execute("INSERT INTO Tag (name) VALUES (?)", (n,)).lastrowid
            print(f"SUCCESS: Tag '{n}' (ID: {id})")
    except sqlite3.IntegrityError:
        print("ERR: Tag exists")


def list_tags():
    with get_db() as c:
        rows = c.execute("SELECT * FROM Tag").fetchall()
    if not rows:
        return print("INFO: No tags.")
    for r in rows:
        print(f"[{r['id']}] {r['name']}")


def del_tag(id):
    with get_db() as c:
        c.execute("DELETE FROM Tag WHERE id=?", (id,))
        print(f"SUCCESS: Tag {id} deleted")

# --- LINK ---


def link(tid, eid):
    try:
        with get_db() as c:
            c.execute(
                "INSERT INTO TaskTag (task_id, tag_id) VALUES (?, ?)", (tid, eid))
            print(f"SUCCESS: Tag {eid} linked to Task {tid}")
    except sqlite3.IntegrityError:
        print("ERR: Bad Link")

# --- CLI ---


def cli():
    p = argparse.ArgumentParser()
    s = p.add_subparsers(dest="cmd")

    ps = s.add_parser("p")
    g = ps.add_mutually_exclusive_group(required=True)
    g.add_argument("--add", action="store_true")
    g.add_argument("--list", action="store_true")
    g.add_argument("--update", type=int, metavar="ID")
    g.add_argument("--delete", type=int, metavar="ID")
    ps.add_argument("--name")
    ps.add_argument("--desc")

    ts = s.add_parser("t")
    g = ts.add_mutually_exclusive_group(required=True)
    g.add_argument("--add", action="store_true")
    g.add_argument("--list", action="store_true")
    g.add_argument("--update", type=int, metavar="ID")
    g.add_argument("--delete", type=int, metavar="ID")
    ts.add_argument("--title")
    ts.add_argument("--pid", type=int)
    ts.add_argument("--status")

    es = s.add_parser("e")
    g = es.add_mutually_exclusive_group(required=True)
    g.add_argument("--add", action="store_true")
    g.add_argument("--list", action="store_true")
    g.add_argument("--delete", type=int, metavar="ID")
    es.add_argument("--name")

    vs = s.add_parser("v")
    vs.add_argument("--add", action="store_true", required=True)
    vs.add_argument("--tid", type=int)
    vs.add_argument("--eid", type=int)

    a = p.parse_args()
    if not a.cmd:
        return p.print_help()

    if a.cmd == "p":
        if getattr(a, 'add'):
            add_proj(a.name, getattr(a, 'desc', None)
                     ) if a.name else print("ERR: --name")
        elif getattr(a, 'list'):
            list_projs()
        elif getattr(a, 'update') is not None:
            upd_proj(a.update, a.name, getattr(a, 'desc', None))
        elif getattr(a, 'delete') is not None:
            del_proj(a.delete)
    elif a.cmd == "t":
        if getattr(a, 'add'):
            add_task(a.title, a.pid) if a.title and a.pid else print(
                "ERR: --title, --pid")
        elif getattr(a, 'list'):
            list_tasks(getattr(a, 'pid', None))
        elif getattr(a, 'update') is not None:
            upd_task(a.update, getattr(a, 'title', None),
                     getattr(a, 'status', None))
        elif getattr(a, 'delete') is not None:
            del_task(a.delete)
    elif a.cmd == "e":
        if getattr(a, 'add'):
            add_tag(a.name) if a.name else print("ERR: --name")
        elif getattr(a, 'list'):
            list_tags()
        elif getattr(a, 'delete') is not None:
            del_tag(a.delete)
    elif a.cmd == "v":
        if getattr(a, 'add'):
            link(a.tid, a.eid) if a.tid and a.eid else print(
                "ERR: --tid, --eid")


if __name__ == '__main__':
    cli()
