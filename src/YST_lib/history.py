import os
import sqlite3
import time

METRIC_KEYS = (
    "subs",
    "channel_views",
    "channel_videos",
    "video_views",
    "video_likes",
    "video_comments",
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recorded_at INTEGER NOT NULL,
    channel_id TEXT NOT NULL,
    video_id TEXT,
    subs INTEGER NOT NULL DEFAULT 0,
    channel_views INTEGER NOT NULL DEFAULT 0,
    channel_videos INTEGER NOT NULL DEFAULT 0,
    video_views INTEGER NOT NULL DEFAULT 0,
    video_likes INTEGER NOT NULL DEFAULT 0,
    video_comments INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_snapshots_channel_time
    ON snapshots (channel_id, video_id, recorded_at);
"""

ADD_COLUMN = {
    "video_title": "ALTER TABLE snapshots ADD COLUMN video_title TEXT",
    "video_duration": "ALTER TABLE snapshots ADD COLUMN video_duration INTEGER",
    "video_published_at": "ALTER TABLE snapshots ADD COLUMN video_published_at INTEGER",
    "subs_hidden": "ALTER TABLE snapshots ADD COLUMN subs_hidden INTEGER DEFAULT 0",
}

# Statement literal, so no SQL is ever built at runtime. test_insert_matches_columns
# fails if a column is added to METRIC_KEYS or ADD_COLUMN without updating it.
INSERT_SNAPSHOT = (
    "INSERT INTO snapshots ("
    "recorded_at, channel_id, video_id, "
    "subs, channel_views, channel_videos, video_views, video_likes, video_comments, "
    "video_title, video_duration, video_published_at, subs_hidden"
    ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
)


def migrate(connection):
    existing = {row["name"] for row in connection.execute("PRAGMA table_info(snapshots)")}
    for column, statement in ADD_COLUMN.items():
        if column not in existing:
            connection.execute(statement)
    connection.commit()


def connect(db_path, shared=False):
    """`shared` allows other threads to use the connection, for the API server.

    The caller has to serialise access; the server does it with a lock.
    """
    folder = os.path.dirname(db_path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    connection = sqlite3.connect(db_path, check_same_thread=not shared)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    migrate(connection)
    return connection


def record(connection, channel_id, video_id, values, meta=None):
    meta = meta or {}
    row = [int(time.time()), channel_id, video_id or ""]
    row += [int(values.get(key, 0) or 0) for key in METRIC_KEYS]
    row += [
        meta.get("video_title"),
        meta.get("video_duration"),
        meta.get("video_published_at"),
        int(bool(meta.get("subs_hidden", False))),
    ]
    connection.execute(INSERT_SNAPSHOT, row)
    connection.commit()
    return row[0]


def latest(connection, channel_id, video_id=None):
    query = "SELECT * FROM snapshots WHERE channel_id = ? AND video_id = ? ORDER BY recorded_at DESC, id DESC LIMIT 1"
    row = connection.execute(query, (channel_id, video_id or "")).fetchone()
    return dict(row) if row else None


def window(connection, channel_id, video_id=None, hours=24, limit=1000):
    since = int(time.time()) - int(hours * 3600)
    if video_id is None:
        query = (
            "SELECT * FROM snapshots WHERE channel_id = ? AND recorded_at >= ? "
            "ORDER BY recorded_at ASC, id ASC LIMIT ?"
        )
        rows = connection.execute(query, (channel_id, since, limit)).fetchall()
    else:
        query = (
            "SELECT * FROM snapshots WHERE channel_id = ? AND video_id = ? AND recorded_at >= ? "
            "ORDER BY recorded_at ASC, id ASC LIMIT ?"
        )
        rows = connection.execute(query, (channel_id, video_id, since, limit)).fetchall()
    return [dict(row) for row in rows]


def series(connection, channel_id, key, video_id=None, hours=24, limit=1000):
    if key not in METRIC_KEYS:
        raise ValueError(f"Unknown metric '{key}'")
    return [(row["recorded_at"], row[key]) for row in window(connection, channel_id, video_id, hours, limit)]


def changes(connection, channel_id, video_id=None, hours=24):
    rows = window(connection, channel_id, video_id, hours)
    if len(rows) < 2:
        return {}
    first, last = rows[0], rows[-1]
    span = max(last["recorded_at"] - first["recorded_at"], 1)
    return {
        key: {
            "current": last[key],
            "previous": first[key],
            "change": last[key] - first[key],
            "per_hour": round((last[key] - first[key]) / span * 3600, 2),
        }
        for key in METRIC_KEYS
    }


def delta(previous, values):
    if not previous:
        return {}
    return {
        key: int(values.get(key, 0) or 0) - int(previous.get(key, 0) or 0)
        for key in METRIC_KEYS
    }


def count(connection, channel_id=None):
    if channel_id:
        row = connection.execute(
            "SELECT COUNT(*) AS total FROM snapshots WHERE channel_id = ?", (channel_id,)
        ).fetchone()
    else:
        row = connection.execute("SELECT COUNT(*) AS total FROM snapshots").fetchone()
    return row["total"]