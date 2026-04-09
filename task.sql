-- Task CLI v0.0.1 | Schema: task.sql
-- Author: Jean Carlos Tomicha Ressa | License: MIT
-- Design: Schema-first, zero-dependency, integrity-enforced.

PRAGMA foreign_keys = ON; -- Enforce referential integrity per connection

-- Projects: Top-level containers for tasks
CREATE TABLE IF NOT EXISTS Project (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tasks: Core work items with lifecycle, priority & hierarchy
CREATE TABLE IF NOT EXISTS Task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'todo' CHECK(status IN ('todo', 'in_progress', 'done', 'cancelled')),
    priority INTEGER NOT NULL DEFAULT 2 CHECK(priority IN (1, 2, 3)), -- 1=High, 2=Med, 3=Low
    due_date TEXT, -- ISO 8601 recommended (YYYY-MM-DD)
    project_id INTEGER NOT NULL,
    parent_id INTEGER, -- Enables subtasks; NULL = top-level
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES Project(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES Task(id) ON DELETE SET NULL
);

-- Tags: Reusable labels for cross-project filtering
CREATE TABLE IF NOT EXISTS Tag (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE -- Case-insensitive uniqueness
);

-- TaskTag: N:M junction table. WITHOUT ROWID optimizes storage & lookup speed.
CREATE TABLE IF NOT EXISTS TaskTag (
    task_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (task_id, tag_id),
    FOREIGN KEY (task_id) REFERENCES Task(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES Tag(id) ON DELETE CASCADE
) WITHOUT ROWID;

-- Indexes: Optimize frequent query patterns
CREATE INDEX IF NOT EXISTS idx_prj_stat ON Task(project_id, status); -- Filter by project + status
CREATE INDEX IF NOT EXISTS idx_date ON Task(due_date) WHERE due_date IS NOT NULL; -- Partial index for active deadlines

-- Trigger: Auto-maintain updated_at on task modifications
CREATE TRIGGER IF NOT EXISTS tr_upd AFTER UPDATE ON Task FOR EACH ROW
BEGIN
    UPDATE Task SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;