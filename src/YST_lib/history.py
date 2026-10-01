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

COLUMNS = ", ".join(METRIC_KEYS)


def connect(db_path):
    folder = os.path.dirname(db_path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    return connection


def record(connection, channel_id, video_id, values):
    row = [int(time.time()), channel_id, video_id or ""]
    row += [int(values.get(key, 0) or 0) for key in METRIC_KEYS]
    placeholders = ", ".join("?" * (3 + len(METRIC_KEYS)))
    connection.execute(
        f"INSERT INTO snapshots (recorded_at, channel_id, video_id, {COLUMNS}) "
        f"VALUES ({placeholders})",
        row,
    )
    connection.commit()
    return row[0]


def latest(connection, channel_id, video_id=None):
    query = "SELECT * FROM snapshots WHERE channel_id = ? AND video_id = ? ORDER BY recorded_at DESC, id DESC LIMIT 1"
    row = connection.execute(query, (channel_id, video_id or "")).fetchone()
    return dict(row) if row else None


def window(connection, channel_id, video_id=None, hours=24, limit=1000):
    since = int(time.time()) - int(hours * 3600)
    query = (
        "SELECT * FROM snapshots WHERE channel_id = ? AND video_id = ? AND recorded_at >= ? "
        "ORDER BY recorded_at ASC, id ASC LIMIT ?"
    )
    rows = connection.execute(query, (channel_id, video_id or "", since, limit)).fetchall()
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


def count(connection, channel_id=None):
    if channel_id:
        row = connection.execute(
            "SELECT COUNT(*) AS total FROM snapshots WHERE channel_id = ?", (channel_id,)
        ).fetchone()
    else:
        row = connection.execute("SELECT COUNT(*) AS total FROM snapshots").fetchone()
    return row["total"]