import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "douyin_downloader.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_url TEXT NOT NULL,
            nickname TEXT DEFAULT '',
            interval_hours INTEGER NOT NULL DEFAULT 6,
            enabled INTEGER NOT NULL DEFAULT 1,
            last_run TEXT,
            next_run TEXT,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            user_url TEXT NOT NULL,
            nickname TEXT DEFAULT '',
            video_count INTEGER DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'running',
            message TEXT DEFAULT '',
            started_at TEXT NOT NULL,
            finished_at TEXT
        );
    """)
    # Ensure default settings exist
    for key, default in [("cookie", ""), ("download_path", os.path.expanduser("~/Desktop/DouyinDownloader/downloads"))]:
        conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, default))
    conn.commit()
    conn.close()

# --- Settings ---

def get_setting(key):
    conn = get_conn()
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else None

def get_all_settings():
    conn = get_conn()
    rows = conn.execute("SELECT key, value FROM settings").fetchall()
    conn.close()
    return {r["key"]: r["value"] for r in rows}

def set_setting(key, value):
    conn = get_conn()
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

# --- Tasks ---

def create_task(user_url, interval_hours, nickname=""):
    now = datetime.now().isoformat(timespec="seconds")
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO tasks (user_url, nickname, interval_hours, created_at) VALUES (?, ?, ?, ?)",
        (user_url, nickname, interval_hours, now)
    )
    task_id = cur.lastrowid
    conn.commit()
    conn.close()
    return task_id

def get_all_tasks():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_task(task_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_task(task_id, **kwargs):
    allowed = {"user_url", "nickname", "interval_hours", "enabled", "last_run", "next_run"}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return
    sets = ", ".join(f"{k} = ?" for k in fields)
    vals = list(fields.values()) + [task_id]
    conn = get_conn()
    conn.execute(f"UPDATE tasks SET {sets} WHERE id = ?", vals)
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = get_conn()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def get_enabled_tasks():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM tasks WHERE enabled = 1").fetchall()
    conn.close()
    return [dict(r) for r in rows]

# --- History ---

def create_history(user_url, task_id=None, nickname=""):
    now = datetime.now().isoformat(timespec="seconds")
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO history (task_id, user_url, nickname, status, started_at) VALUES (?, ?, ?, 'running', ?)",
        (task_id, user_url, nickname, now)
    )
    hist_id = cur.lastrowid
    conn.commit()
    conn.close()
    return hist_id

def finish_history(hist_id, status, video_count=0, message=""):
    now = datetime.now().isoformat(timespec="seconds")
    conn = get_conn()
    conn.execute(
        "UPDATE history SET status = ?, video_count = ?, message = ?, finished_at = ? WHERE id = ?",
        (status, video_count, message, now, hist_id)
    )
    conn.commit()
    conn.close()

def get_history(limit=100, offset=0):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM history ORDER BY started_at DESC LIMIT ? OFFSET ?",
        (limit, offset)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_history_count():
    conn = get_conn()
    row = conn.execute("SELECT COUNT(*) as cnt FROM history").fetchone()
    conn.close()
    return row["cnt"]

def delete_history(hist_id):
    conn = get_conn()
    conn.execute("DELETE FROM history WHERE id = ?", (hist_id,))
    conn.commit()
    conn.close()

def get_history_by_task(task_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM history WHERE task_id = ? ORDER BY started_at DESC",
        (task_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
