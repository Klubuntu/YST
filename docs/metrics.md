# Metrics and history

Back to the [README](../README.md).

## Choosing which metrics to log

By default every metric is logged. Narrow it down with `-enable_log`, or keep
everything except a few with `-disable_log` — both take a comma- or
space-separated list:

```bash
# only these two
python src/YST.py -channel_id=UCifZaTQPiHE2QRgEwDNfhug -video_id=C7REVNM_EWY -enable_log subs, video_views

# everything except these two
python src/YST.py -channel_id=UCifZaTQPiHE2QRgEwDNfhug -video_id=C7REVNM_EWY -disable_log subs, video_views
```

| Key              | File                      | Meaning                          |
| ---------------- | ------------------------- | -------------------------------- |
| `subs`           | `channel_subscribers.txt` | Channel subscribers              |
| `channel_views`  | `channel_viewsCount.txt`  | Total channel views              |
| `channel_videos` | `channel_videoCount.txt`  | Published videos                 |
| `video_views`    | `video_views.txt`         | Views of the tracked video       |
| `video_likes`    | `video_likes.txt`         | Likes of the tracked video       |
| `video_comments` | `video_comments.txt`      | Comments of the tracked video    |

Short aliases are accepted too (`subscribers`, `views`, `likes`, `comments`,
`videos`, …), keys are case-insensitive, and `-list_logs=True` prints the full
list with its output file. The two flags are mutually exclusive, an unknown
metric stops the tool with the valid names, and the active selection is echoed
on start-up. Disabled metrics are neither written to disk nor printed in
`-log_mode=True`.

Channels that hide their subscriber count show `hidden by the channel` instead
of a misleading zero.

Member counts and subscriber status are not available at all: YouTube removed
them from the Data API v3, and the dashboard states this instead of leaving it
to be assumed.

## History and deltas

Every refresh is stored as a snapshot in a local SQLite database
(`data/yst.db` by default), which makes growth measurable over time. Snapshots
cost no extra API calls, because the numbers already fetched for `txt/` are
written to the database instead.

Deltas appear next to each metric automatically once a second snapshot exists:

```
(01-10-2026) - 19:33:41
Subscribers: 693 (0)
Channel Views: 152 486 (+12)
Video Views: 111 200 (+553)
```

Video length and publication date are shown below the statistics when they are
known:

```
Video: (Pora to naprawić !) Konfiguracja Archa
Published: 29-01-2023   Length: 3:17:37
```

```bash
# snapshots every 5 minutes into a custom database
python src/YST.py -channel_id=UC... -video_id=... -snapshot_time=300 -db data/mine.db
```

## Dashboard

`-dashboard=True` adds a summary of the last `-history` hours with per-hour
rates and a sparkline:

```
Last 24h:
Video Likes: +39 (+2/h)
Video Views: +10 647 (+546/h)
Video Views trend: ▁▁▁▁▁▁▁▁▂▂▂▂▂▃▃▃▄▄▄▅▅▅▆▆▆▇▇█
```

```bash
python src/YST.py -channel_id=UCifZaTQPiHE2QRgEwDNfhug -video_id=C7REVNM_EWY -sleep_time=60 -dashboard=True
```

A fresh database prints `no snapshots in the last Nh` rather than an empty
summary.

## Charts

`-chart=True` draws block charts of the selected window next to the dashboard,
so a longer window stays readable instead of collapsing into a sparkline:

```bash
python src/YST.py monitor UCifZaTQPiHE2QRgEwDNfhug -dashboard=True -chart=True -history=168
```

```
Video Views:
▁▁▁▁▁▁▁▁▁▁▂▄▆█████▁
▁▁▁▁▁▁▁▁▁▁▁▁▁▂▄▆█▁
1 000                             20 773
```

Charts need at least two snapshots in the window and are skipped otherwise.

## Export

`-export` writes the stored snapshots and exits, so it costs no API calls:

```bash
# every video of the channel, last 24 hours, default folder
python src/YST.py -channel_id=UCifZaTQPiHE2QRgEwDNfhug -export csv

# one video, last 7 days, into reports/
python src/YST.py -channel_id=UC... -video_id=C7REVNM_EWY -history 168 -export json -export_path reports
```

```csv
recorded_at,channel_id,video_id,subs,channel_views,channel_videos,video_views,video_likes,video_comments
1790883289,UCifZaTQPiHE2QRgEwDNfhug,Xknt3_QJY7o,693,152486,434,43,3,0
```

The columns are `recorded_at` (Unix time), `channel_id`, `video_id` and the
metric keys.

## HTML report

`-report=True` writes a self-contained HTML file to the export folder with one
SVG line chart per metric, the min/max range and a table of the stored values:

```bash
python src/YST.py -channel_id=UC... -video_id=... -report=True -history=168
```

The report has no external assets, so it can be shared as a single file. Charts
are skipped for metrics with fewer than two snapshots.

## Generated folders

Created next to the working directory and ignored by git:

| Folder     | Contents                                    |
| ---------- | ------------------------------------------- |
| `txt/`     | Latest value of every logged metric         |
| `data/`    | `yst.db`, the snapshot history               |
| `exports/` | CSV, JSON and HTML output                    |