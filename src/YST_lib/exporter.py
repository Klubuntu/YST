import csv
import io
import json
import os

from YST_lib.history import METRIC_KEYS, window

EXPORT_COLUMNS = ("recorded_at", "channel_id", "video_id") + METRIC_KEYS


def to_csv(connection, channel_id, video_id=None, hours=24):
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(EXPORT_COLUMNS)
    for row in window(connection, channel_id, video_id, hours):
        writer.writerow([row.get(column, "") for column in EXPORT_COLUMNS])
    return buffer.getvalue()


def to_json(connection, channel_id, video_id=None, hours=24):
    payload = [
        {column: row.get(column, "") for column in EXPORT_COLUMNS}
        for row in window(connection, channel_id, video_id, hours)
    ]
    return json.dumps(payload, indent=2)


WRITERS = {"csv": to_csv, "json": to_json}


def render(connection, export_format, channel_id, video_id=None, hours=24):
    return WRITERS[export_format](connection, channel_id, video_id, hours)


def save(
    connection,
    export_format,
    channel_id,
    video_id=None,
    hours=24,
    folder="exports",
    stamp="",
):
    os.makedirs(folder, exist_ok=True)
    target = os.path.join(folder, f"{channel_id}_{stamp}.{export_format}")
    try:
        with open(target, "w", encoding="utf-8", newline="") as f:
            f.write(render(connection, export_format, channel_id, video_id, hours))
    except OSError as e:
        raise OSError(f"Cannot write '{target}': {e}") from e
    return target