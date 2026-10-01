import sqlite3
import time

import pytest

from YST_lib.history import (
    ADD_COLUMN,
    INSERT_SNAPSHOT,
    METRIC_KEYS,
    changes,
    connect,
    count,
    delta,
    latest,
    record,
    series,
    window,
)


def make_values(**overrides):
    values = {key: 0 for key in METRIC_KEYS}
    values.update(
        {
            "subs": 100,
            "channel_views": 1000,
            "channel_videos": 10,
            "video_views": 500,
            "video_likes": 20,
            "video_comments": 5,
        }
    )
    values.update(overrides)
    return values


@pytest.fixture()
def database(tmp_path):
    connection = connect(str(tmp_path / "yst.db"))
    yield connection
    connection.close()


def seed(connection, values, channel="UCtest", video="abc123", recorded_at=None):
    connection.execute(
        "INSERT INTO snapshots (recorded_at, channel_id, video_id, subs, channel_views, "
        "channel_videos, video_views, video_likes, video_comments) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            recorded_at if recorded_at is not None else int(time.time()),
            channel,
            video,
            *(values[key] for key in METRIC_KEYS),
        ),
    )
    connection.commit()


def test_connect_creates_folder(tmp_path):
    target = str(tmp_path / "nested" / "yst.db")
    connection = connect(target)
    assert count(connection) == 0
    connection.close()


def test_record_and_latest_roundtrip(database):
    record(database, "UCtest", "abc123", make_values(video_views=500))
    row = latest(database, "UCtest", "abc123")
    assert row["video_views"] == 500
    assert row["channel_id"] == "UCtest"


def test_latest_without_snapshots_returns_none(database):
    assert latest(database, "UCmissing", "abc123") is None


def test_latest_returns_most_recent(database):
    seed(database, make_values(video_views=1), recorded_at=1000)
    seed(database, make_values(video_views=2), recorded_at=2000)
    assert latest(database, "UCtest", "abc123")["video_views"] == 2


def test_record_uses_current_time_and_defaults(database):
    record(database, "UCtest", "abc123", {})
    row = latest(database, "UCtest", "abc123")
    assert row["video_views"] == 0
    assert row["recorded_at"] <= int(time.time())


def test_delta_against_previous_snapshot():
    previous = make_values(video_views=500)
    current = make_values(video_views=553, video_likes=22)
    result = delta(previous, current)
    assert result["video_views"] == 53
    assert result["video_likes"] == 2
    assert result["subs"] == 0


def test_delta_without_previous_is_empty():
    assert delta(None, make_values()) == {}


def test_changes_over_window(database):
    now = int(time.time())
    seed(database, make_values(video_views=100), recorded_at=now - 7200)
    seed(database, make_values(video_views=200), recorded_at=now)
    result = changes(database, "UCtest", "abc123", hours=24)
    assert result["video_views"]["change"] == 100
    assert result["video_views"]["current"] == 200


def test_changes_needs_two_snapshots(database):
    seed(database, make_values())
    assert changes(database, "UCtest", "abc123") == {}


def test_changes_per_hour_rate(database):
    now = int(time.time())
    seed(database, make_values(video_views=0), recorded_at=now - 3600)
    seed(database, make_values(video_views=3600), recorded_at=now)
    result = changes(database, "UCtest", "abc123", hours=24)
    assert result["video_views"]["per_hour"] == 3600


def test_window_filters_by_age(database):
    now = int(time.time())
    seed(database, make_values(), recorded_at=now - 7200)
    seed(database, make_values(), recorded_at=now)
    assert len(window(database, "UCtest", "abc123", hours=1)) == 1
    assert len(window(database, "UCtest", "abc123", hours=24)) == 2


def test_window_without_video_returns_every_video(database):
    seed(database, make_values(), video="one")
    seed(database, make_values(), video="two")
    assert len(window(database, "UCtest", None, hours=24)) == 2
    assert len(window(database, "UCtest", "one", hours=24)) == 1


def test_series_returns_pairs(database):
    now = int(time.time())
    seed(database, make_values(video_views=10), recorded_at=now - 60)
    seed(database, make_values(video_views=20), recorded_at=now)
    assert series(database, "UCtest", "video_views", "abc123", hours=24) == [
        (now - 60, 10),
        (now, 20),
    ]


def test_series_rejects_unknown_metric(database):
    try:
        series(database, "UCtest", "nope")
    except ValueError:
        return
    raise AssertionError("expected ValueError")

def test_migrate_adds_video_columns_to_existing_database(tmp_path):
    target = str(tmp_path / "old.db")
    legacy = sqlite3.connect(target)
    legacy.execute(
        "CREATE TABLE snapshots (id INTEGER PRIMARY KEY AUTOINCREMENT, recorded_at INTEGER, "
        "channel_id TEXT, video_id TEXT, subs INTEGER, channel_views INTEGER, "
        "channel_videos INTEGER, video_views INTEGER, video_likes INTEGER, video_comments INTEGER)"
    )
    legacy.commit()
    legacy.close()

    connection = connect(target)
    columns = {row["name"] for row in connection.execute("PRAGMA table_info(snapshots)")}
    assert {"video_title", "video_duration", "video_published_at"} <= columns
    connection.close()


def test_insert_matches_columns():
    # INSERT_SNAPSHOT is a statement literal, so it cannot drift from the column
    # lists on its own. Assert it here instead.
    columns_part, values_part = INSERT_SNAPSHOT.split(") VALUES ")
    columns = [c.strip() for c in columns_part.split("(", 1)[1].split(",")]
    placeholders = [v.strip() for v in values_part.strip("()").split(",")]
    expected = ["recorded_at", "channel_id", "video_id"] + list(METRIC_KEYS) + list(ADD_COLUMN)
    assert columns == expected
    assert placeholders == ["?"] * len(expected)


def test_record_stores_video_meta(database):
    record(
        database,
        "UCtest",
        "abc123",
        make_values(),
        {"video_title": "Title", "video_duration": 3723, "video_published_at": 1674993600},
    )
    row = latest(database, "UCtest", "abc123")
    assert row["video_title"] == "Title"
    assert row["video_duration"] == 3723
    assert row["video_published_at"] == 1674993600


def test_record_stores_hidden_subscribers(database):
    record(database, "UCtest", "abc123", make_values(), {"subs_hidden": True})
    assert latest(database, "UCtest", "abc123")["subs_hidden"] == 1


def test_record_defaults_hidden_subscribers_to_zero(database):
    record(database, "UCtest", "abc123", make_values())
    assert latest(database, "UCtest", "abc123")["subs_hidden"] == 0
