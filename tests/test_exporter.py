import json
import os
import time

import pytest

from YST_lib.exporter import render, save
from YST_lib.history import METRIC_KEYS, connect


@pytest.fixture()
def database(tmp_path):
    connection = connect(str(tmp_path / "yst.db"))
    values = {key: 0 for key in METRIC_KEYS}
    values.update({"subs": 100, "video_views": 500})
    connection.execute(
        "INSERT INTO snapshots (recorded_at, channel_id, video_id, subs, channel_views, "
        "channel_videos, video_views, video_likes, video_comments) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (int(time.time()), "UCtest", "abc123", *(values[key] for key in METRIC_KEYS)),
    )
    connection.commit()
    yield connection
    connection.close()


def test_csv_has_header_and_row(database):
    content = render(database, "csv", "UCtest", "abc123")
    lines = content.strip().splitlines()
    assert lines[0].startswith("recorded_at,channel_id,video_id,subs")
    assert len(lines) == 2
    assert "UCtest" in lines[1]
    assert "UCtest" in lines[1]


def test_json_is_parsable_list_of_snapshots(database):
    payload = json.loads(render(database, "json", "UCtest", "abc123"))
    assert isinstance(payload, list)
    assert payload[0]["video_views"] == 500
    assert payload[0]["channel_id"] == "UCtest"


def test_render_rejects_unknown_format(database):
    with pytest.raises(KeyError):
        render(database, "excel", "UCtest", "abc123")


def test_save_creates_timestamped_file(database, tmp_path):
    folder = str(tmp_path / "exports")
    target = save(database, "csv", "UCtest", "abc123", 24, folder, "20260101-000000")
    assert target.endswith(os.path.join(folder, "UCtest_20260101-000000.csv"))
    with open(target, encoding="utf-8") as f:
        assert "recorded_at" in f.read()
